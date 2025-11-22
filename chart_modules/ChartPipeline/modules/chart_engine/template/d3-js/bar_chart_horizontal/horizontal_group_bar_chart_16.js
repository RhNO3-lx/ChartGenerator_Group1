/*
REQUIREMENTS_BEGIN
{
    "chart_type": "Horizontal Group Bar Chart",
    "chart_name": "horizontal_group_bar_chart_16",
    "is_composite": false,
    "required_fields": ["x", "y", "group"],
    "required_fields_type": [["categorical"], ["numerical"], ["categorical"]],
    "required_fields_range": [[2, 30], [0, "inf"], [2, 2]],
    "required_fields_icons": ["group"],
    "required_other_icons": [],
    "required_fields_colors": ["group"],
    "required_other_colors": ["primary"],
    "supported_effects": ["shadow", "radius_corner", "stroke", "spacing"],
    "min_height": 400,
    "min_width": 400,
    "background": "none",
    "icon_mark": "none",
    "icon_label": "none",
    "has_x_axis": "no",
    "has_y_axis": "no"
}
REQUIREMENTS_END
*/

function wrapAndShrinkText(textSel, content, maxWidth, initialFs, lineHeight = 1.2) {
  const svg = d3.select(textSel.node().ownerSVGElement);
  const measurer = svg.append('text')
      .style('font-family', textSel.style('font-family'))
      .style('font-weight', textSel.style('font-weight'))
      .style('font-size', `${initialFs}px`)
      .style('visibility', 'hidden')
      .attr('x', -9999).attr('y', -9999);

  let fs = initialFs;
  const words = content.split(/\s+/);
  let lines = [];

  function layoutLines() {
    lines = [];
    let current = [];
    words.forEach(w => {
      const testLine = current.concat(w).join(' ');
      measurer.text(testLine);
      if (measurer.node().getBBox().width > maxWidth && current.length > 0) {
        lines.push(current.join(' '));
        current = [w];
      } else {
        current.push(w);
      }
    });
    if (current.length) lines.push(current.join(' '));
  }

  while (true) {
    layoutLines();
    const tooWide = lines.some(line => {
      measurer.text(line);
      return measurer.node().getBBox().width > maxWidth;
    });
    if (!tooWide) break;
    const widest = d3.max(lines, line => {
      measurer.text(line);
      return measurer.node().getBBox().width;
    });
    const scale = maxWidth / widest;
    fs = Math.floor(fs * scale);
    measurer.style('font-size', `${fs}px`);
  }
  measurer.remove();

  textSel.style('font-size', `${fs}px`).selectAll('tspan').remove();
  lines.forEach((line, i) => {
    textSel.append('tspan')
      .attr('x', +textSel.attr('x'))
      .attr('dy', i === 0 ? textSel.attr('dy') : fs * lineHeight)
      .text(line);
  });
}


// 双向组群水平条形图实现（同 x, y, group）- 使用 D3.js
function makeChart(containerSelector, data) {
    // --- 1. 数据与变量提取 ---
    const chartData = data.data.data;
    const columns   = data.data.columns || [];
    const variables = data.variables || {};
    const typography = data.typography || {};
    const colors     = data.colors || {};

    // 宽高与 margin
    const width  = variables.width  || 800;
    const height = variables.height || 600;
    const margin = { top: 60, right: 20, bottom: 30, left: 20 };

    // --- 2. 确定字段名 ---
    let xField = 'x', yField = 'y', groupField = 'group';
    columns.forEach(col => {
        if (col.role === 'x')      xField = col.name;
        if (col.role === 'y')      yField = col.name;
        if (col.role === 'group')  groupField = col.name;
    });

    // --- 3. 分类、组别与量度 ---
    const categories = [...new Set(chartData.map(d => d[xField]))];
    const groups     = [...new Set(chartData.map(d => d[groupField]))];
    if (groups.length !== 2) {
        console.warn('Expect exactly 2 groups for diverging effect.');
    }

    // 计算最大绝对值，用于对称的 x 轴
    const absMax = d3.max(chartData, d => Math.abs(d[yField])) * 1.05;

    // --- 4. 比例尺 ---
    const y0 = d3.scaleBand()
                 .domain(categories)
                 .range([0, height - margin.top - margin.bottom])
                 .padding(0.05);

    const y1 = d3.scaleBand()
                 .domain(groups)
                 .range([0, y0.bandwidth()])
                 .padding(0.1);

    const x = d3.scaleLinear()
                .domain([-absMax, absMax])
                .range([0, width - margin.left - margin.right]);

    const centerX = x(0);

    // --- 5. 创建 SVG ---
    const svg = d3.select(containerSelector)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // 中心线
    g.append('line')
     .attr('x1', centerX).attr('x2', centerX)
     .attr('y1', 0).attr('y2', y0.range()[1])
     .attr('stroke', '#000').attr('stroke-width', 1).style('opacity', 0.3);


     // --- 5.5 添加左右背景 ---
    const getColor = d => (
    colors.field?.[d]
    || (groups.indexOf(d) === 0
        ? (colors.other?.primary || '#4682B4')
        : (colors.other?.secondary || '#5F9EA0'))
    );

    // 左侧背景：取 group0 颜色，转 HSL，饱和度乘 0.5，亮度加 0.4
    const leftHsl = d3.hsl(getColor(groups[0]));
    leftHsl.l = Math.min(1, Math.max(leftHsl.l - 0.5,0.2));
    const bgLeftColor = leftHsl.formatHex();
    leftHsl.s = Math.max(0, leftHsl.s * 0.5);
    leftHsl.l = Math.min(1, Math.min(leftHsl.l + 0.3,0.8));
    const LeftColor = leftHsl.formatHex();

    // 右侧背景：同理
    const rightHsl = d3.hsl(getColor(groups[1]));
    rightHsl.l = Math.min(1, Math.max(rightHsl.l - 0.1,0.2));
    const bgRightColor = rightHsl.formatHex();
    rightHsl.s = Math.max(0, rightHsl.s * 0.5);
    rightHsl.l = Math.min(1, Math.min(rightHsl.l + 0.4,0.8));
    const RightColor = rightHsl.formatHex();

    const innerHeight = height;
    const bgY      = -1;

    // 左半区背景
    svg.insert('rect', ':first-child')
    .attr('x', 0)
    .attr('y', bgY)
    .attr('width', centerX + margin.left)
    .attr('height', innerHeight)
    .attr('fill', bgLeftColor);

    // 右半区背景
    svg.insert('rect', ':first-child')
    .attr('x', centerX + margin.left)
    .attr('y', bgY)
    .attr('width', centerX + margin.left)
    .attr('height', innerHeight)
    .attr('fill', bgRightColor);

    // --- 6. 绘制条形 ---
    const groupG = g.selectAll('.category')
        .data(chartData)
        .enter()
        .append('g')
        .attr('transform', d => `translate(0,${y0(d[xField])})`);

    // 为每个 data 画 rect
    groupG.append('rect')
        .attr('x', d => {
            const v = d[yField];
            return groups.indexOf(d[groupField]) === 0 ? x(-v) : centerX;
        })
        .attr('y', d => 0)
        .attr('width', d => Math.abs(x(d[yField]) - centerX))
        .attr('height', y1.bandwidth() * 2)
        .attr('fill', d => {
            // group 0 -> 左侧，group 1 -> 右侧
            return (groups.indexOf(d[groupField]) === 0 ? LeftColor : RightColor);
        })
        .attr('rx', variables.has_rounded_corners ? 3 : 0)
        .attr('filter', variables.has_shadow ? 'url(#shadow)' : null);

    // --- 7. 类别标签 ---
    // 1) 初始字号
    let labelFs = 14;
    // 2) 测量所有标签在初始字号下的宽度
    const maxAllowed = y1.bandwidth() * 2 * 0.95;
    const measure = svg.append('text')
    .attr('class', 'label-measurer')
    .style('font-family', typography.label?.font_family || 'Arial')
    .style('font-weight', typography.label?.font_weight || 'bold')
    .style('font-size', `${labelFs}px`)
    .style('visibility', 'hidden');

    let maxW = 0;
    categories.forEach(cat => {
    measure.text(cat);
    const w = measure.node().getBBox().width;
    if (w > maxW) maxW = w;
    });
    measure.remove();

    // 3) 如果超限，按比例缩小
    if (maxW > maxAllowed) {
    labelFs = labelFs * (maxAllowed / maxW);
    }

    g.selectAll('.cat-label')
        .data(categories)
        .enter()
        .append('text')
        .attr('transform', d => {
            const x = centerX + labelFs / 2;
            const y = y0(d) + y1.bandwidth();
            return `translate(${x},${y}) rotate(90)`;
        })
        .attr('dy', '0.35em')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'bottom')
        .style('font-family', 'Arial')
        .style('font-size', `${labelFs}px`)
        .style('font-weight', 'bold')
        .text(d => d);

    // --- 8. 数值注记（可选） ---
    const fmt = d3.format('~g');
    const padding = 7;
    // 最大字号：两层子带高度之和
    const maxFs = y1.bandwidth() * 2;

    // 1) 先在 SVG 上创建一个临时 text，用于测量
    const measurer = svg.append('text')
    .attr('class', 'measurer')
    .style('font-family', 'Times New Roman')
    .style('font-weight', 'bold')
    .style('font-size', `${maxFs}px`)
    .style('visibility', 'hidden');

    // 2) 遍历所有数据，计算每条注记在 maxFs 下的实际宽度、可用宽度，并得出允许的字号
    let uniformFs = maxFs;
    chartData.forEach(d => {
    const txt = fmt(d[yField]);
    measurer.text(txt);
    const txtW = measurer.node().getBBox().width;

    // 计算该条形的实际宽度
    const v      = d[yField];
    const isLeft = groups.indexOf(d[groupField]) === 0;
    const start  = isLeft ? x(-v) : centerX;
    const end    = isLeft ? centerX    : x(v);
    const barW   = Math.abs(end - start);

    // 可用宽度：如果要放在内侧则 barW - padding，否则无限制
    const placeInside = barW >= maxFs;
    const availW = placeInside ? (barW - 18) : Infinity;

    // 当前文本在 maxFs 下如果宽度超限，需要缩至 maxFs * availW / txtW
    if (txtW > availW) {
        const allowedFs = Math.floor(maxFs * (availW / txtW));
        uniformFs = Math.min(uniformFs, allowedFs);
    }
    });
    // 清理临时测量节点
    measurer.remove();

    // 3) 用统一的 uniformFs 来绘制所有文本
    groupG.append('text')
    .attr('x', d => {
        const v      = d[yField];
        const isLeft = groups.indexOf(d[groupField]) === 0;
        const start  = isLeft ? x(-v) : centerX;
        const end    = isLeft ? centerX    : x(v);
        // 如果 barW < maxFs，就认为放外侧
        const barW = Math.abs(end - start);
        const offset = padding / 2;
        if (barW < maxFs) {
        return isLeft ? start - offset : end + offset;
        }
        return isLeft ? start + offset : end - offset;
    })
    .attr('y', () => y1.bandwidth())
    .attr('dy', '0.35em')
    .attr('text-anchor', d => {
        const v      = d[yField];
        const isLeft = groups.indexOf(d[groupField]) === 0;
        const start  = isLeft ? x(-v) : centerX;
        const end    = isLeft ? centerX    : x(v);
        return Math.abs(end - start) < maxFs
        ? (isLeft ? 'end' : 'start')
        : (isLeft ? 'start' : 'end');
    })
    .style('font-family', 'Times New Roman')
    .style('font-weight', 'bold')
    .style('font-size', `${uniformFs}px`)
    .style('fill', d => {
        const v      = d[yField];
        const isLeft = groups.indexOf(d[groupField]) === 0;
        const start  = isLeft ? x(-v) : centerX;
        const end    = isLeft ? centerX    : x(v);
        return Math.abs(end - start) < maxFs
        ? (isLeft ? LeftColor : RightColor)
        : (isLeft ? bgLeftColor : bgRightColor);
    })
    .text(d => fmt(d[yField]));

    // --- 9. 创建图例 ---

    const getText = d => d; 

    columns.forEach(col => {
        if (col.role === 'y')      y_description = col.description;
    });
    // 左侧图例（组 0）
    svg.append("text")
        .attr("class", "legend-left")
        .attr("x", width / 4) 
        .attr("y", margin.top / 3)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .style("font-family", 'Times New Roman')
        .style("font-size", '27px')
        .style("font-weight", 'bold')
        .style("fill", 'white')
        .text(getText(groups[0]));

    // 右侧图例（组 1）
    svg.append("text")
        .attr("class", "legend-right")
        .attr("x", width * 3 / 4)
        .attr("y", margin.top / 3)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .style("font-family", 'Times New Roman')
        .style("font-size", '27px')
        .style("font-weight", 'bold')
        .style("fill", 'white')
        .text(getText(groups[1]));

    const maxLegendWidth = width / 2 * 0.95;

    // 遍历两侧图例，测量并等比缩小字体
    ['.legend-left', '.legend-right'].forEach(selector => {
    const textSel = svg.select(selector);
    // 初始字体大小要和 append 时一致
    let fs = parseFloat(textSel.style('font-size'));
    // 先明确设置一次，确保测量精准
    textSel.style('font-size', `${fs}px`);
    // 测量实际宽度
    const bbox = textSel.node().getBBox();
    if (bbox.width > maxLegendWidth) {
        // 等比缩小
        fs = fs * (maxLegendWidth / bbox.width);
        svg.select('.legend-left').style('font-size', `${fs}px`);
        svg.select('.legend-right').style('font-size', `${fs}px`);
    }
    });

    svg.append("text")
        .attr("class", "legend-description")
        .attr("x", width / 2) 
        .attr("y", margin.top * 4 / 5)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .style("font-family", 'Arial')
        .style("font-size", '15px')
        .style("fill", 'white')
        .text(y_description);

    // 调用 wrapAndShrinkText，使 y_description 不超出中间区域
    wrapAndShrinkText(
        desc,                              // 目标 <text> 节点
        y_description,                     // 要显示的文本
        width - margin.left - margin.right,// 最大可用宽度
        15,                                // 初始字号
        0.5                                // 行高倍数
    );



    return svg.node();
}
