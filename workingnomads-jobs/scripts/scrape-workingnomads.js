/**
 * Working Nomads 远程工作爬取脚本
 * - 支持按类别筛选
 * - 支持关键词过滤（前端开发相关）
 * - 支持获取大量职位
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  url: 'https://www.workingnomads.com/jobs',
  outputDir: path.join(__dirname, '..', 'output', 'workingnomads'),
  defaultLimit: 50
};

// 前端开发相关关键词
const FRONTEND_KEYWORDS = [
  'react', 'vue', 'vuejs', 'angular', 'svelte',
  'javascript', 'typescript',
  'frontend', 'front-end', 'front end',
  'ui', 'ux',
  'css', 'sass', 'less', 'tailwind',
  'html', 'web developer', 'web design',
  'responsive', 'web app', ' SPA'
];

async function scrapeJobs(options = {}) {
  const { 
    category = null, 
    keywords = [], 
    limit = CONFIG.defaultLimit, 
    saveToFile = true,
    filterFrontend = false
  } = options;
  
  console.log('🚀 启动浏览器...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
  });
  const page = await context.newPage();
  
  let targetUrl = CONFIG.url;
  if (category) {
    targetUrl = `${CONFIG.url}?category=${category}`;
  }
  
  console.log(`📄 正在访问: ${targetUrl}`);
  await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2000);
  
  const allJobs = await extractAllJobs(page);
  
  let filteredJobs = allJobs;
  if (filterFrontend || keywords.length > 0) {
    const filterKeys = filterFrontend ? FRONTEND_KEYWORDS : keywords;
    filteredJobs = allJobs.filter(job => {
      const searchText = (job.title + ' ' + job.description).toLowerCase();
      return filterKeys.some(key => searchText.includes(key.toLowerCase()));
    });
    console.log(`🔍 关键词过滤: ${allJobs.length} → ${filteredJobs.length} 个职位`);
  }
  
  const jobs = await fetchJobDetails(page, filteredJobs.slice(0, limit));
  
  await browser.close();
  
  console.log(`\n✅ 成功获取 ${jobs.length} 个职位`);
  
  const parsedJobs = parseJobData(jobs);
  
  if (saveToFile && parsedJobs.length > 0) {
    saveToFileSystem(parsedJobs, { category, keywords: filterFrontend ? '前端开发' : keywords });
  }
  
  return parsedJobs;
}

async function extractAllJobs(page) {
  const allLinks = await page.$$eval('a', links => 
    links.map(l => ({
      text: l.innerText?.trim() || '',
      href: l.href
    })).filter(l => l.text && l.text.length > 10 && l.text.length < 200)
  );
  
  return allLinks.filter(l => {
    const text = l.text.toLowerCase();
    return (
      l.href.includes('/jobs/') && 
      !text.includes('remote') && 
      !text.includes('subscribe') &&
      !text.includes('post') &&
      !text.includes('premium') &&
      !text.includes('company') &&
      !l.href.includes('#')
    );
  });
}

async function fetchJobDetails(page, jobs) {
  const results = [];
  
  for (let i = 0; i < jobs.length; i++) {
    const link = jobs[i];
    console.log(`📄 爬取 ${i+1}/${jobs.length}: ${link.text.substring(0, 40)}...`);
    
    try {
      await page.goto(link.href, { waitUntil: 'domcontentloaded', timeout: 10000 });
      await page.waitForTimeout(800);
      
      const job = await page.evaluate(() => ({
        title: document.querySelector('h1, .job-title')?.innerText?.trim() || '',
        description: document.body.innerText,
        url: window.location.href
      }));
      
      if (job.title) {
        results.push(job);
      }
      
      await page.goto(CONFIG.url, { waitUntil: 'networkidle', timeout: 15000 });
      await page.waitForTimeout(800);
      
    } catch (err) {
      console.warn(`⚠️  失败: ${err.message}`);
    }
  }
  
  return results;
}

function parseJobData(jobs) {
  return jobs.map((job, i) => {
    const lines = job.description.split('\n').filter(l => l.trim());
    
    let company = 'N/A';
    for (let j = 0; j < lines.length; j++) {
      if (lines[j].includes('Report') && j + 1 < lines.length) {
        const next = lines[j + 1].trim();
        if (next && !next.includes('Apply') && next.length < 50 && !next.match(/^(Senior|Mid|Junior|Apply|http)/)) {
          company = next;
          break;
        }
      }
    }
    
    let type = '全职';
    if (job.description.includes('Freelance / Contract')) type = '项目制/合同';
    else if (job.description.includes('Part-time')) type = '兼职';
    
    let location = 'Remote';
    const locMatch = job.description.match(/(Europe|EMEA|US|North America|Latin America|APAC|EU CET|Worldwide)/);
    if (locMatch) location = locMatch[0];
    
    let level = 'N/A';
    const levelMatch = job.description.match(/(Senior|Mid|Junior|Lead|Principal|Entry)/i);
    if (levelMatch) level = levelMatch[0] + ' Level';
    
    let salary = '未说明';
    const salaryMatch = job.description.match(/€\$[\d,]+(\s*-\s*[\d,]+)?(\s*(per hour|per month|per year|onboarding fee))/i);
    if (salaryMatch) salary = salaryMatch[0];
    
    const matchedKeywords = FRONTEND_KEYWORDS.filter(key => 
      (job.title + ' ' + job.description).toLowerCase().includes(key.toLowerCase())
    );
    
    return {
      index: i + 1,
      company: company,
      title: job.title,
      type: type,
      location: location,
      level: level,
      salary: salary,
      matchedKeywords: [...new Set(matchedKeywords)],
      url: job.url
    };
  });
}

function saveToFileSystem(jobs, options = {}) {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
  
  const timestamp = new Date().toISOString().split('T')[0];
  
  const jsonPath = path.join(CONFIG.outputDir, `jobs-${timestamp}.json`);
  fs.writeFileSync(jsonPath, JSON.stringify({
    scrapedAt: new Date().toISOString(),
    count: jobs.length,
    filter: options,
    jobs: jobs
  }, null, 2), 'utf8');
  console.log(`💾 JSON: ${jsonPath}`);
  
  let md = `# Working Nomads ${options.keywords || '全部'} 远程职位列表\n`;
  md += `> 爬取时间: ${new Date().toLocaleString('zh-CN')}\n`;
  md += `> 职位数量: ${jobs.length}\n`;
  if (options.keywords) {
    md += `> 筛选条件: ${options.keywords.join(', ')}\n`;
  }
  md += `\n---\n\n`;
  
  md += `| # | 公司 | 职务 | 类型 | 地点 | 等级 | 匹配技能 |\n`;
  md += `|---|---|---|---|---|---|---|\n`;
  
  jobs.forEach(job => {
    const keywords = job.matchedKeywords.slice(0, 4).join(', ');
    md += `| ${job.index} | ${job.company} | ${job.title} | ${job.type} | ${job.location} | ${job.level} | ${keywords} |\n`;
  });
  
  const mdPath = path.join(CONFIG.outputDir, `jobs-${timestamp}.md`);
  fs.writeFileSync(mdPath, md, 'utf8');
  console.log(`📝 Markdown: ${mdPath}`);
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {
    category: null,
    filterFrontend: args.includes('--frontend'),
    limit: parseInt(args.find(a => a.startsWith('--limit'))?.split('=')[1] || CONFIG.defaultLimit)
  };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--category' || args[i] === '-c') {
      options.category = args[i + 1];
      i++;
    }
  }
  
  const filterName = options.filterFrontend ? '前端开发' : (options.category || '全部');
  console.log(`🎯 Working Nomads 职位爬虫\n`);
  console.log(`📋 筛选条件: ${filterName}\n`);
  
  scrapeJobs(options)
    .then(jobs => {
      if (jobs && jobs.length > 0) {
        console.log('\n📊 结果预览 (前5个):\n');
        jobs.slice(0, 5).forEach(job => {
          console.log(`${job.index}. ${job.title} @ ${job.company}`);
          console.log(`   ${job.type} | ${job.location} | ${job.matchedKeywords.slice(0,3).join(', ')}\n`);
        });
        console.log(`\n总计: ${jobs.length} 个职位`);
      }
    });
}

module.exports = { scrapeJobs, CONFIG, FRONTEND_KEYWORDS };
