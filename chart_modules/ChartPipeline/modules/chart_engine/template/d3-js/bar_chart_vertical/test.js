/*
REQUIREMENTS_BEGIN
{
    "chart_type": "test",
    "chart_name": "test",
    "is_composite": false,
    "required_fields": ["x", "y", "group"],
    "required_fields_type": [["categorical"], ["numerical"], ["categorical"]],
    "required_fields_range": [[2, 7], ["-inf", "inf"], [2, 2]],
    "required_fields_icons": [],
    "required_other_icons": [],
    "required_fields_colors": ["group"],
    "required_other_colors": [],
    "supported_effects": ["shadow", "radius_corner", "gradient", "stroke", "spacing"],
    "min_height": 400,
    "min_width": 400,
    "background": "light",
    "icon_mark": "none",
    "icon_label": "none",
    "has_x_axis": "no",
    "has_y_axis": "no"
}
REQUIREMENTS_END
*/

// 垂直分组条形图实现 - 带有百分比变化指示器
function makeChart(containerSelector, data) {
    // ---------- 1. 数据准备 ----------
    // 提取数据和配置
    const jsonData = data;                          
    const chartData = jsonData.data.data || [];          
    const variables = jsonData.variables || {};     
    const typography = {     
        title: { font_family: "Arial", font_size: "18px", font_weight: "bold" },
        label: { font_family: "Arial", font_size: "16px", font_weight: "normal" },
        description: { font_family: "Arial", font_size: "14px", font_weight: "normal" },
        annotation: { font_family: "Arial", font_size: "8px", font_weight: "normal" }
    };
    const colors = jsonData.colors || { 
        text_color: "#333333", 
        field: {
            "2011 Sales": "#154360", // 深蓝色 (2011)
            "2012 Sales": "#3498DB", // 浅蓝色 (2012)
            "YoY Change": "#C0392B"  // 红色 (百分比变化)
        },
        other: { 
            primary: "#4682B4",
            percentage_indicator: "#C0392B" // 百分比指示器的红色
        } 
    };
    const images = jsonData.images || { field: {}, other: {} };
    const dataColumns = jsonData.data.columns || [];
    
    // 如果不存在，添加副标题字段
    typography.subtitle = typography.subtitle || typography.description;
    
    // 设置视觉效果变量
    variables.has_rounded_corners = variables.has_rounded_corners || false;
    variables.has_shadow = variables.has_shadow || false;
    variables.has_gradient = variables.has_gradient || false;
    variables.has_stroke = variables.has_stroke || false;
    variables.has_spacing = variables.has_spacing || false;
    
    // 清除容器
    d3.select(containerSelector).html("");
    
    // 添加数值格式化函数
    const formatValue = (value) => {
        if (value >= 1000000000) {
            return d3.format("~g")(value / 1000000000) + "B";
        } else if (value >= 1000000) {
            return d3.format("~g")(value / 1000000) + "M";
        } else if (value >= 1000) {
            return d3.format("~g")(value / 1000) + "K";
        } else {
            return d3.format("~g")(value);
        }
    }
    
    // ---------- 2. 尺寸和布局设置 ----------
    // 设置图表尺寸和边距
    const width = variables.width || 800;
    const height = variables.height || 500;
    
    // 边距：上，右，下，左
    const margin = { 
        top: 90,    // 标题和副标题的空间
        right: 40,   // 右侧标签的空间
        bottom: 90,  // x轴和标签的空间
        left: 80     // y轴和标签的空间
    };
    
    // 计算实际绘图区域大小
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    // ---------- 3. 提取字段名称和单位 ----------
    let xField, yField, groupField;
    let xUnit = "", yUnit = "";
    
    // 安全提取字段名称
    const xColumn = dataColumns.find(col => col.role === "x");
    const yColumn = dataColumns.find(col => col.role === "y");
    const groupColumn = dataColumns.find(col => col.role === "group");
    
    if (xColumn) xField = xColumn.name;
    if (yColumn) yField = yColumn.name;
    if (groupColumn) groupField = groupColumn.name;
    
    // 获取字段单位
    xUnit = xColumn?.unit === "none" ? "" : (xColumn?.unit || "");
    yUnit = yColumn?.unit === "none" ? "" : (yColumn?.unit || "");
    
    // ---------- 4. 数据处理 ----------
    // 使用提供的数据
    let useData = chartData;
    
    // 获取x轴和分组的唯一值
    const xValues = [...new Set(useData.map(d => d[xField]))];
    let groupValues = [...new Set(useData.map(d => d[groupField]))];
    
    // 确保我们只有两个组字段：第一个组是左侧柱子，第二个组是右侧柱子
    if (groupValues.length !== 2) {
        console.warn("此图表需要恰好2个组字段：用于左侧和右侧柱状图。");
    }
    
    // 第一个组是左侧柱子，第二个组是右侧柱子
    const leftBarGroup = groupValues[0];
    const rightBarGroup = groupValues[1];
    
    // ---------- 5. 创建SVG容器 ----------
    const svg = d3.select(containerSelector)
        .append("svg")
        .attr("width", "100%")
        .attr("height", height)
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("style", "max-width: 100%; height: auto;")
        .attr("xmlns", "http://www.w3.org/2000/svg")
        .attr("xmlns:xlink", "http://www.w3.org/1999/xlink");
    
    // ---------- 6. 创建视觉效果 ----------
    const defs = svg.append("defs");
    
    // 如果需要，创建阴影滤镜
    if (variables.has_shadow) {
        const filter = defs.append("filter")
            .attr("id", "shadow")
            .attr("filterUnits", "userSpaceOnUse")
            .attr("width", "200%")
            .attr("height", "200%");
        
        filter.append("feGaussianBlur")
            .attr("in", "SourceAlpha")
            .attr("stdDeviation", 3);
        
        filter.append("feOffset")
            .attr("dx", 2)
            .attr("dy", 2)
            .attr("result", "offsetblur");
        
        const feMerge = filter.append("feMerge");
        feMerge.append("feMergeNode");
        feMerge.append("feMergeNode").attr("in", "SourceGraphic");
    }
    
    // ---------- 7. 创建图表区域 ----------
    const chart = svg.append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);
    
    // ---------- 8. 创建比例尺 ----------
    // X比例尺（分类）用于主分类
    const xScale = d3.scaleBand()
        .domain(xValues)
        .range([0, innerWidth])
        .padding(0.2);
    
    // 分组比例尺，用于每个类别内的细分
    const groupScale = d3.scaleBand()
        .domain([0, 1]) // 只有两个柱子，左侧和右侧
        .range([0, xScale.bandwidth()])
        .padding(0.2); // 增加同一维度柱子之间的间隙
    
    // 计算动态文本大小的函数
    const calculateFontSize = (text, maxWidth, baseSize = 12) => {
        // 估算每个字符的平均宽度 (假设为baseSize的60%)
        const avgCharWidth = baseSize * 0.6;
        // 计算文本的估计宽度
        const textWidth = text.length * avgCharWidth;
        // 如果文本宽度小于最大宽度，返回基础大小
        if (textWidth < maxWidth) {
            return baseSize;
        }
        // 否则，按比例缩小字体大小
        return Math.max(8, Math.floor(baseSize * (maxWidth / textWidth)));
    };
    
    // 检查是否应该显示x轴标签
    const shouldShowLabel = (text) => {
        const maxWidth = xScale.bandwidth() * 2; // 两个柱子宽度之和的两倍
        const avgCharWidth = 12 * 0.6; // 使用基础字体大小12
        const textWidth = text.length * avgCharWidth;
        return textWidth <= maxWidth;
    };

    const dataMax = d3.max(useData, d => +d[yField]);
    const dataMin = d3.min(useData, d => +d[yField]);

    // 给正负两端都留 10% 的空白
    const paddingFactor = 0.1;
    const yMax = dataMax > 0
    ? dataMax * (1 + paddingFactor)
    : dataMax * (1 - paddingFactor);
    const yMin = dataMin < 0
    ? dataMin * (1 + paddingFactor * -1)
    : 0;

    // 再对齐到整十/整百等
    const niceMax = Math.ceil(yMax / 10) * 10;
    const niceMin = Math.floor(yMin / 10) * 10;

    const yScale = d3.scaleLinear()
        .domain([niceMin, niceMax])
        .range([innerHeight, 0]);
    
    // ---------- 9. 创建坐标轴 ----------
    // 底部的X轴
    chart.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0, ${innerHeight})`)
        .call(d3.axisBottom(xScale).tickSize(0))
        .call(g => {
            g.select(".domain").remove();
            
            // 第一步：找出最长的标签并计算统一的字体大小
            let maxLabelLength = 0;
            const allLabels = [];
            
            // 收集所有标签并找出最长的一个
            g.selectAll(".tick text").each(function(d) {
                const labelText = d.toString();
                allLabels.push(labelText);
                if (labelText.length > maxLabelLength) {
                    maxLabelLength = labelText.length;
                }
            });
            
            // 使用最长标签计算合适的统一字体大小
            const maxWidth = xScale.bandwidth() * 1.2 ; 
            const longestLabel = allLabels.reduce((a, b) => a.length > b.length ? a : b, "");
            const uniformFontSize = calculateFontSize(longestLabel, maxWidth);
            
            // 第二步：应用统一字体大小，必要时进行换行处理
            g.selectAll(".tick text")
                .style("font-family", typography.label.font_family)
                .style("font-size", `${uniformFontSize}px`) // 应用统一的字体大小
                .style("font-weight", typography.label.font_weight)
                .style("fill", colors.text_color)
                .each(function(d) {
                    const text = d3.select(this);
                    
                    // 检查使用统一字体大小后，文本是否仍然超过可用宽度
                    if (this.getComputedTextLength() > maxWidth) {
                        // 如果仍然太长，应用文本换行
                        wrapText(text, d.toString(), maxWidth, 1.1);
                    }
                });
        });
    
    // 文本换行助手函数
    function wrapText(text, str, width, lineHeight) {
        const words = str.split(/\s+/).reverse();
        let word;
        let line = [];
        let lineNumber = 0;
        const y = text.attr("y");
        const dy = parseFloat(text.attr("dy") || 0);
        let tspan = text.text(null).append("tspan")
            .attr("x", 0)
            .attr("y", y)
            .attr("dy", dy + "em");
        
        // 如果没有空格可分割，按字符分割
        if (words.length <= 1) {
            const chars = str.split('');
            let currentLine = '';
            
            for (let i = 0; i < chars.length; i++) {
                currentLine += chars[i];
                tspan.text(currentLine);
                
                if (tspan.node().getComputedTextLength() > width && currentLine.length > 1) {
                    // 当前行过长，回退一个字符并换行
                    currentLine = currentLine.slice(0, -1);
                    tspan.text(currentLine);
                    
                    // 创建新行
                    currentLine = chars[i];
                    tspan = text.append("tspan")
                        .attr("x", 0)
                        .attr("y", y)
                        .attr("dy", ++lineNumber * lineHeight + dy + "em")
                        .text(currentLine);
                }
            }
        } else {
            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));
                
                if (tspan.node().getComputedTextLength() > width && line.length > 1) {
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = text.append("tspan")
                        .attr("x", 0)
                        .attr("y", y)
                        .attr("dy", ++lineNumber * lineHeight + dy + "em")
                        .text(word);
                }
            }
        }
        
        // 调整标签位置以保持居中
        if (lineNumber > 0) {
            text.selectAll("tspan").attr("y", parseFloat(y));
        }
    }
    
    
    // ---------- 10. 绘制图例 ----------
    // 图例
    const legendData = [
        { key: leftBarGroup, color: colors.field[leftBarGroup] || "#154360" },
        { key: rightBarGroup, color: colors.field[rightBarGroup] || "#3498DB" }
    ];
    
    // 计算图例项宽度
    const tempSvg = d3.select(containerSelector).append("svg").style("visibility", "hidden");
    const legendItemWidths = [];
    let totalLegendWidth = 0;
    const legendPadding = 20; // 图例项之间的间距
    
    legendData.forEach(item => {
        const tempText = tempSvg.append("text")
            .style("font-family", typography.label.font_family)
            .style("font-size", "12px")
            .style("font-weight", typography.label.font_weight)
            .text(item.key.toString().replace(" Sales", ""));
        
        const textWidth = tempText.node().getBBox().width;
        const legendItemWidth = 15 + 5 + textWidth + legendPadding; // 色块(15) + 间距(5) + 文本宽度 + 右侧填充
        
        legendItemWidths.push(legendItemWidth);
        totalLegendWidth += legendItemWidth;
        
        tempText.remove();
    });
    
    tempSvg.remove();
    
    // 创建图例并居中放置
    const legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", `translate(${(width - totalLegendWidth + legendPadding + 40) / 2}, 80)`);
    
    // 为每个组添加一个图例项，水平排列
    let legendOffset = 0;
    const rectSize = 15;
    const legendY  = innerHeight + margin.bottom * 0.5;

    legendData.forEach((item, i) => {
    const legendItem = legend.append("g")
        .attr("class", "legend-item")
        .attr("transform", `translate(${legendOffset}, 0)`);

    // 色块，中心对齐到 legendY
    legendItem.append("rect")
        .attr("x", 0)
        .attr("y", legendY - rectSize / 2)  // 上移半个高度
        .attr("width", rectSize)
        .attr("height", rectSize)
        .attr("fill", item.color);

    // 文本，基线改为 middle，y 直接用 legendY
    legendItem.append("text")
        .attr("x", rectSize + 5)           // 色块右侧 + 5px 间距
        .attr("y", legendY)
        .attr("dominant-baseline", "middle")
        .style("font-family", typography.label.font_family)
        .style("font-size", "12px")
        .style("font-weight", typography.label.font_weight)
        .style("fill", colors.text_color)
        .text(item.key.toString().replace(" Sales", ""));

    legendOffset += legendItemWidths[i];
    });
    
    // ---------- 11. 绘制条形图中x对应的框 ----------
    // 对每个 x 类别，计算该组柱顶最高位置
    const groupTopY = {};
    xValues.forEach(xValue => {
        const tops = [];
        [leftBarGroup, rightBarGroup].forEach(grp => {
            const d = useData.find(d => d[xField] === xValue && d[groupField] === grp);
            if (d) {
                const val = d[yField];
                // 正值顶端 yScale(val)，负值顶端 yScale(0)
                tops.push(val >= 0 ? yScale(val) : yScale(0));
            }
        });
        // 最“高”即最小的 y
        groupTopY[xValue] = d3.min(tops);
    });

    const groupPadding = 4; // 框与bar顶部的间距
    const frameBottomY = innerHeight + margin.bottom * 0.2; // 所有组框的底部 Y 坐标（统一）
    const frameWidth = xScale.bandwidth(); // 一组bar占的总宽度

    xValues.forEach(xValue => {
        const topY = groupTopY[xValue] - groupPadding; // 向上留一点空隙
        const xCenter = xScale(xValue) + xScale.bandwidth() / 2;
        const frameX = xCenter - frameWidth / 2;
        const frameHeight = frameBottomY - topY;

        chart.append("rect")
            .attr("x", frameX - groupPadding / 2)
            .attr("y", topY)
            .attr("width", frameWidth + groupPadding)
            .attr("height", frameHeight)
            .attr('rx', 6)
            .attr("fill", "rgba(0,0,0,0.05)");
    });



    // ---------- 12. 绘制条形图 ----------
    const shadow_padding = 3;
    // 渐变定义助手：为每个 grp+index 生成一个独有 ID
    function createBarGradient(id, baseColor) {
    const grad = defs.append("linearGradient")
        .attr("id", id)
        .attr("x1", "0%").attr("y1", "0%")
        .attr("x2", "0%").attr("y2", "100%");
    // 顶部（0%） 更浅
    grad.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", d3.color(baseColor).brighter(0.5).formatHex());
    // 底部（100%） 更深
    grad.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", d3.color(baseColor).darker(0.5).formatHex());
    }

    // 在绘制柱子前，先为左右两种颜色生成渐变
    const leftColor  = colors.field[leftBarGroup]  || "#154360";
    const rightColor = colors.field[rightBarGroup] || "#3498DB";
    createBarGradient("grad-left",  leftColor);
    createBarGradient("grad-right", rightColor);
    // 为每个x类别创建一个组
    const xGroups = chart.selectAll(".x-group")
        .data(xValues)
        .enter()
        .append("g")
        .attr("class", "x-group")
        .attr("transform", d => `translate(${xScale(d)}, 0)`);
    
    // 绘制条形图
    xValues.forEach(xValue => {
        const xData = useData.filter(d => d[xField] === xValue);

        // 左/右柱子数据同之前
        [ leftBarGroup, rightBarGroup ].forEach((grp, idx) => {
            const barData = xData.find(d => d[groupField] === grp);
            if (!barData) return;

            // 计算当前柱子的 x,y,width,height
            const xPos = xScale(xValue) + (idx === 0 ?  xScale.bandwidth() / 4 - groupScale.bandwidth() / 2: xScale.bandwidth() * 3 / 4 - groupScale.bandwidth() / 2);
            const barW = groupScale.bandwidth();

            // 柱体阴影
            chart.append("rect")
                .attr("x", barData[yField] >= 0 ? xPos - shadow_padding : xPos + shadow_padding)
                .attr("y", barData[yField] >= 0 ? yScale(barData[yField]) + shadow_padding : yScale(0))
                .attr("width", barW)
                .attr("height", Math.abs(yScale(barData[yField]) - yScale(0)) - shadow_padding)
                .attr("fill", "rgba(128, 128, 128, 0.7)")
            
            // 柱体
            chart.append("rect")
                .attr("x", xPos)
                .attr("y", barData[yField] >= 0 ? yScale(barData[yField]) : yScale(0))
                .attr("width", barW)
                .attr("height", Math.abs(yScale(barData[yField]) - yScale(0)))
                // 用 ID 引用对应渐变：左组用 grad-left，右组用 grad-right
                .attr("fill", `url(#${idx===0 ? "grad-left" : "grad-right"})`)
        });
    });

    // --- 13 预计算：徽章统一宽度 & 每组最高柱顶 Y ---
    const padding = 2;  // 徽章内边距
    const allValues = [];

    // 收集所有要标记的数值文本
    xValues.forEach(xValue => {
    [leftBarGroup, rightBarGroup].forEach(grp => {
        const d = useData.find(d => d[xField] === xValue && d[groupField] === grp);
        if (d) allValues.push(formatValue(d[yField]));
    });
    });

    // 测量最宽文本
    const measurer = svg.append('text')
        .style('font-family', typography.annotation.font_family)
        .style('font-size', typography.annotation.font_size)
        .style('visibility', 'hidden');
    let maxTextW = 0;
    allValues.forEach(txt => {
    measurer.text(txt);
    maxTextW = Math.max(maxTextW, measurer.node().getBBox().width);
    });
    measurer.remove();

    // 徽章尺寸
    const badgeWidth  = maxTextW + padding * 2;
    const badgeHeight = parseFloat(typography.annotation.font_size) * 1.2 + padding * 2; // 行高 * 字号 + 上下内边距


    // --- 13.2 绘制指示牌 ---

    xValues.forEach(xValue => {
        const topY = groupTopY[xValue];
        [leftBarGroup, rightBarGroup].forEach((grp, idx) => {
            const d = useData.find(d => d[xField] === xValue && d[groupField] === grp);
            if (!d) return;

            // 柱子布局
            const xPos = xScale(xValue) + (idx === 0 ?  xScale.bandwidth() / 4 - groupScale.bandwidth() / 2: xScale.bandwidth() * 3 / 4 - groupScale.bandwidth() / 2);
            const val   = d[yField];
            // 条顶 Y
            const barTopY = val >= 0 ? yScale(val) : yScale(0);
            // 柱高
            const barH = Math.abs(yScale(val) - yScale(0));

            // 徽章在条顶上方：多加一个与 barH 成比例的小偏移
            const extraOffset = barH * 0.02;  // 5% 的高度差
            const badgeY      = barTopY - badgeHeight - 6 - extraOffset;
            const badgeX      = xPos + groupScale.bandwidth() / 2;

            // 1) 画连线
            chart.append('line')
                .attr('x1', badgeX)
                .attr('y1', badgeY + badgeHeight)
                .attr('x2', badgeX)
                .attr('y2', barTopY + padding)
                .attr('stroke', "black")
                .attr('stroke-width', 1)
                .style('opacity', 0.8);
            
            chart.append('rect')
                .attr('x', badgeX - padding)
                .attr('y', barTopY + padding)
                .attr('width', padding * 2)
                .attr('height', padding * 2)
                .attr('rx', 6)
                .attr('fill', "white");

            // 2) 徽章容器
            const gBadge = chart.append('g')
                .attr('transform', `translate(${badgeX - badgeWidth / 2},${badgeY})`);

            // 背景圆角矩形
            gBadge.append('rect')
                .attr('width', badgeWidth)
                .attr('height', badgeHeight)
                .attr('rx', 6)
                .attr('fill', colors.field[grp]);

            // 居中白色文本
            gBadge.append('text')
                .attr('x', badgeWidth / 2)
                .attr('y', badgeHeight / 2)
                .attr('dy', '0.35em')
                .attr('text-anchor', 'middle')
                .style('font-family', typography.annotation.font_family)
                .style('font-size', typography.annotation.font_size)
                .style('font-weight', typography.annotation.font_weight)
                .style('fill', '#fff')
                .text(formatValue(val));
        });
    });



    // 添加x轴处的长黑横线
    chart.append("line")
        .attr("x1", 0)
        .attr("y1", yScale(0))
        .attr("x2", innerWidth)
        .attr("y2", yScale(0))
        .attr("stroke", "grey")
        .attr("stroke-width", 2);
    // 返回SVG节点
    return svg.node();
}