
    const puppeteer = require('puppeteer');
    const fs = require('fs');
    const path = require('path');

    (async () => {
        const browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();
        await page.setViewport({ width: 600, height: 600 });
        
        try {
            // 加载HTML文件
            await page.goto('file://' + path.resolve('/data/minzhi/code/ChartGalaxyDemo/tmp/d3_svg_93356a32-c619-4762-bc7c-d5bfa8601fd1/chart.html'), { waitUntil: 'networkidle0' });
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // 检查是否是ECharts图表
            const isECharts = await page.evaluate(() => {
                return typeof echarts !== 'undefined';
            });
            
            let svgContent;
            
            if (isECharts) {
                // ECharts特定处理
                await page.evaluate(() => {
                    const chart = echarts.getInstanceByDom(
                        document.querySelector('#chart-container')
                    );
                    if (chart) {
                        chart.setOption({animation: false});
                        try {
                            chart.setOption({renderer: 'svg'});
                        } catch (e) {
                            console.log('无法设置SVG渲染器:', e.message);
                        }
                    }
                });
                
                // 尝试从ECharts获取SVG
                svgContent = await page.evaluate(() => {
                    const chart = echarts.getInstanceByDom(
                        document.querySelector('#chart-container')
                    );
                    return chart ? chart.renderToSVGString() : null;
                });
            }
            
            // 回退到直接SVG提取
            if (!svgContent) {
                svgContent = await page.evaluate(() => {
                    const svg = document.querySelector('#chart-container svg');
                    if (!svg) return null;
                    
                    // 克隆并清理SVG
                    const clone = svg.cloneNode(true);
                    if (!clone.hasAttribute('width')) {
                        clone.setAttribute('width', svg.clientWidth);
                    }
                    if (!clone.hasAttribute('height')) {
                        clone.setAttribute('height', svg.clientHeight);
                    }
                    if (!clone.hasAttribute('viewBox')) {
                        clone.setAttribute('viewBox', `0 0 ${svg.clientWidth} ${svg.clientHeight}`);
                    }
                    return clone.outerHTML;
                });
            }
            
            // 最终回退 - 截图转SVG
            if (!svgContent) {
                const screenshot = await page.screenshot({encoding: 'base64'});
                svgContent = `<svg width="600" height="600" xmlns="http://www.w3.org/2000/svg">
                    <image href="data:image/png;base64,${screenshot}" width="100%" height="100%"/>
                </svg>`;
            }
            
            // 输出SVG内容到stdout
            console.log(svgContent);
            
        } catch (error) {
            console.error('错误:', error);
            process.exit(1);
        } finally {
            await browser.close();
        }
    })();
    