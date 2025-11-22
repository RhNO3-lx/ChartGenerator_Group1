import cairosvg

# SVG 代码（直接使用你提供的透明背景 SVG）
svg_code = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="520" height="130" style="font-family: Arial, 'Liberation Sans', 'DejaVu Sans', sans-serif;">
    <defs>
        <linearGradient id="gradient_5438" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#E2F1F6" />
            <stop offset="100%" stop-color="#bbdee9" />
        </linearGradient>
    </defs>
    <g class="text" fill="#414141">
        <g class="title" transform="translate(26.18, 0)">
            <rect x="0" y="0" width="11" height="110" fill="#3f8aff" transform="translate(-26.18, 0) translate(0, 0)"/>
            <g>
                <text dominant-baseline="hanging" text-anchor="start" style="font-family: Arial; font-size: 28px; font-weight: 700;" transform="translate(0, 0.0)">Google Play Poised to Surpass iOS</text>
                <text dominant-baseline="hanging" text-anchor="start" style="font-family: Arial; font-size: 28px; font-weight: 700;" transform="translate(0, 33.6)">App Store</text>
            </g>
            <g>
                <text dominant-baseline="hanging" text-anchor="start" style="font-family: Arial; font-size: 16px; font-weight: 500;" transform="translate(0, 76.6) translate(0, 0.0)">Total app downloads for Google Play Store and iOS App Store (in</text>
                <text dominant-baseline="hanging" text-anchor="start" style="font-family: Arial; font-size: 16px; font-weight: 500;" transform="translate(0, 76.6) translate(0, 19.2)">millions).</text>
            </g>
        </g>
    </g>
</svg>
"""

# 转换为 PNG（背景透明）
cairosvg.svg2png(bytestring=svg_code.encode('utf-8'), write_to='output.png', output_width=520, output_height=130)