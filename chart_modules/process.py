import os
import time
from datetime import datetime
from threading import Thread
import traceback
from pathlib import Path
import sys
project_root = Path(__file__).parent
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
print("sys.path:",sys.path)

from chart_modules.layout_extraction import get_compatible_extraction
from chart_modules.ChartGalaxy.example_based_generation.generate_infographic import InfographicImageGenerator
from chart_modules.reference_recognize.extract_chart_type import extract_chart_type
from chart_modules.reference_recognize.extract_main_color import extract_main_color
from chart_modules.generate_variation import generate_variation



def conduct_reference_finding(datafile, generation_status):
    print(conduct_reference_finding)
    datafile = os.path.join('processed_data', datafile.replace(".csv", ".json"))

    generation_status['step'] = 'find_reference'
    generation_status['status'] = 'processing'
    generation_status['completed'] = False

    try:
        generation_status["extraction_templates"] = get_compatible_extraction(datafile)
        # print("筛选的模板:", generation_status["extraction_templates"])
        
        
        generation_status['status'] = 'completed'
        generation_status['completed'] = True
        

    except Exception as e:
        generation_status['status'] = 'error'
        generation_status['progress'] = str(e)
        generation_status['completed'] = True
        print("find_reference 出错",e)
        
def conduct_layout_extraction(reference, datafile, generation_status):
    datafile = os.path.join('processed_data', datafile.replace(".csv", ".json"))
    reference = os.path.join('infographics', reference)

    generation_status['step'] = 'layout_extraction'
    generation_status['status'] = 'processing'
    generation_status['completed'] = False
    # print("----------筛选的模板:", generation_status["extraction_templates"])

    try:
        # Step 1: 抽取参考风格
        generation_status['progress'] = '抽取参考信息图表风格...'
        generation_status['style']["colors"], generation_status['style']["bg_color"] = extract_main_color(reference)
        print("提取的颜色: %s %s", generation_status['style']["colors"], generation_status['style']["bg_color"])
        
        # Step 2: 执行图表类型分析 + 模板匹配
        generation_status['progress'] = '分析对应图表类型...'
        generation_status['style']['variation'] = extract_chart_type(reference, generation_status["extraction_templates"])
       
        
        for variation in generation_status['style']['variation']:
            print("variation:",variation)
            thread = Thread(target=generate_variation, args=(generation_status["selected_data"], 
                                                         f"buffer/{generation_status['id']}/{variation[0].split('/')[-1]}.svg", 
                                                         variation,
                                                         generation_status['style']["colors"],
                                                         generation_status['style']["bg_color"],))
            thread.start()
        
        generation_status['status'] = 'completed'
        generation_status['completed'] = True

    except Exception as e:
        generation_status['status'] = 'error'
        generation_status['progress'] = str(e)
        generation_status['completed'] = True
        print("conduct_layout_extraction 出错",e)
    
def conduct_title_generation(datafile, generation_status):
    
    generation_status['step'] = 'title_generation'
    generation_status['status'] = 'processing'
    generation_status['completed'] = False

    try:
        # 生成标题文本
        generation_status['progress'] = '生成标题文本中...'
        generator = InfographicImageGenerator()
        generator.output_dir = f"buffer/{generation_status['id']}"
        print("generation_status['style']:",generation_status['style'])
        generation_status['title_options'] = generator.generate_title_option(os.path.join('processed_data', datafile), f"{generation_status['style']['colors']}")
        # generation_status['title_options'] = {'title_0.png': {'title_text': 'App Downloads Growth: iOS vs Google', 'title_prompt': 'Create a text image with the title "App Downloads Growth: iOS vs Google" arranged on two centered lines, with extra blank space above and below the text to ensure the title stands out against a pure white background. The first line should read: "App Downloads Growth:", and the second line: "iOS vs Google". Emphasize the words "Downloads Growth" by enlarging their font size and coloring them with RGB (28, 144, 248) to draw attention, while the rest of the text uses RGB (18, 22, 24) for strong contrast. Integrate a minimalistic blue download arrow icon in place of the "A" in "App", using the same blue as above (RGB 28, 144, 248), shaped to fit seamlessly within the word. Apply a modern, clean sans-serif font style throughout, with bold weight for the emphasized words. Avoid any decorative effects such as cracks, melting, or shading; the design should be flat and clear, ensuring all text and icons use colors strictly from the following palette: [227, 216, 131], [197, 200, 200], [28, 144, 248], [37, 86, 169], [18, 22, 24]. The text lines must follow the specified split and arrangement, and all elements should visually balance for poster titling purposes.'}, 'title_1.png': {'title_text': 'App Store Downloads Growth Comparison', 'title_prompt': 'Create a text image for the title “App Store Downloads Growth Comparison” with the following requirements:  \n— The text must be arranged in exactly two centered lines, with each line containing more than five words. The first line should read: “App Store Downloads Growth”, and the second line should read: “Comparison”. Maintain ample white space above and below the text, with a pure white background.  \n— The words “Downloads” and “Growth” in the first line should be visually emphasized by increasing their font size and using the color RGB(28, 144, 248) for these two words, while the rest of the text uses RGB(18, 22, 24).  \n— Integrate a subtle upward-pointing arrow icon in place of the “w” in “Growth”, using the same blue (RGB(28, 144, 248)) as the emphasized words. The arrow should blend seamlessly with the font, matching the letter’s stroke width.  \n— The font style should be modern and clean, with bold, sans-serif letterforms. Add a slight soft shadow behind the emphasized blue text and the arrow icon using RGB(197, 200, 200) to create a gentle three-dimensional lift, while the rest of the text remains flat. No other shadow or effects should be applied.  \n— Do not use any colors outside the palette: [227, 216, 131], [197, 200, 200], [28,'}, 'title_4.png': {'title_text': 'App Store Growth Over Time', 'title_prompt': 'Create a text image featuring the title "App Store Growth Over Time", arranged strictly as a single line across the center of a pure white background, with ample blank space above and below the text. The text must not be split into multiple lines. Use a modern, clean sans-serif font that conveys a sense of technological advancement and progress. Emphasize the words "Growth" and "Over Time" by using a larger font size for these words compared to the rest of the title, while maintaining consistent font style throughout. All text must use only colors from the following palette: pale gold (RGB 227, 216, 131), soft silver-gray (RGB 197, 200, 200), bright blue (RGB 28, 144, 248), deep blue (RGB 37, 86, 169), and black (RGB 18, 22, 24). For artistic effect, subtly overlay a gentle upward gradient on the text from deep blue at the bottom (RGB 37, 86, 169) to bright blue at the top (RGB 28, 144, 248), symbolizing growth. Integrate a simple upward-pointing arrow icon (in pale gold, RGB 227, 216, 131) into the letter "A" of "App", replacing the horizontal bar of the "A" with the arrow, to visually reinforce the concept of growth. Ensure the icon blends seamlessly with the typography. No other decorative elements'}, 'title_3.png': {'title_text': 'App Downloads Growth: iOS vs Google Play', 'title_prompt': 'Create a high-resolution text image with a pure white background. The title "App Downloads Growth: iOS vs Google Play" should be centered and arranged in exactly two lines, with the first line reading "App Downloads Growth:" and the second line reading "iOS vs Google Play". Leave generous blank space above and below the text, ensuring the layout is visually balanced and uncluttered. \n\nUse a clean, bold, sans-serif font with a modern, tech-inspired feel. For the color palette, select from only these RGB values: [227, 216, 131] (warm gold), [197, 200, 200] (light gray), [28, 144, 248] (vivid blue), [37, 86, 169] (deep blue), and [18, 22, 24] (almost black). Apply the vivid blue ([28, 144, 248]) to the words "Downloads Growth" to emphasize them, using a slightly larger font size for these words. The rest of the text should use the almost black ([18, 22, 24]) for strong contrast.\n\nIntegrate a decorative icon: replace the letter "O" in the word "Downloads" with a stylized download arrow icon encircled, using the deep blue ([37, 86, 169]) for the icon. This icon should be seamlessly integrated into the typography, matching the font’s weight and size. All other text must'}, 'title_2.png': {'title_text': 'App Store Growth Over Time', 'title_prompt': 'Create a text image featuring the title "App Store Growth Over Time" arranged in exactly two lines, with the words split as follows:  \nLine 1: "App Store Growth"  \nLine 2: "Over Time"  \nEnsure there is ample blank space above and below the text, and the background must be pure white.\n\nEmphasize the key words "App Store" by using a larger font size than the rest of the text and coloring these words with the RGB value [28, 144, 248]. The remaining words ("Growth Over Time") should use the color [37, 86, 169]. All text must use only colors from this restricted palette: [227, 216, 131], [197, 200, 200], [28, 144, 248], [37, 86, 169], [18, 22, 24].\n\nIntegrate a subtle icon by replacing the letter "o" in the word "Store" (on the first line) with a stylized app icon shape (rounded square with a slight shine), filled in [227, 216, 131]. The icon should be visually cohesive with the font, at the same scale as the replaced letter, and harmoniously integrated into the word.\n\nUse a clean, modern sans-serif font with smooth, bold lines to convey growth and clarity. Apply a subtle upward gradient effect to the text fill, transitioning from [28, 144, 248'}}
        # 生成标题
        generation_status['progress'] = '绘制标题中...'
        
        for title_option in generation_status['title_options']:
            # TODO 
            thread = Thread(target=generator.generate_image, 
                            args=(generation_status['title_options'][title_option]["title_prompt"],
                                "title",
                                f'buffer/{generation_status["id"]}/{title_option}'))
            thread.start()
        
        
        # print("title_options:", generation_status['title_options'])
        generation_status['status'] = 'completed'
        generation_status['completed'] = True

    except Exception as e:
        generation_status['status'] = 'error'
        generation_status['progress'] = str(e)
        generation_status['completed'] = True
        print(f"title_generation 出错 {e} {traceback.format_exc()}")

def conduct_pictogram_generation(title, generation_status):
    generation_status['step'] = 'pictogram_generation'
    generation_status['status'] = 'processing'
    generation_status['progress'] = '生成配图...'
    generation_status['completed'] = False

    try:
        # 生成配图prompt
        generation_status['progress'] = '生成配图样式中...'
        generator = InfographicImageGenerator()
        generation_status['pictogram_options'] = generator.generate_pictogram_option(generation_status["title_options"][title]["title_text"],generation_status["style"]["colors"])

        # generation_status['pictogram_options'] = {'pictogram_3.png': {'pictogram_prompt': 'Create a visually engaging, professional illustration for an infographic titled "App Downloads Growth: iOS vs Google," using a modern, minimalist flat vector art style with a pure white background. Depict two tall, upward-pointing, stylized bar graphs or growth arrows side by side—one representing iOS and the other representing Google—constructed from app icon-like rounded squares stacked vertically. Ensure the left column uses harmonious blues ([28, 144, 248] and [37, 86, 169]) for iOS and the right uses a balanced mix of warm gold, neutral gray, and deep blackish tones ([227, 216, 131], [197, 200, 200], [18, 22, 24]) for Google. Add subtle, abstract visual cues—like dotted lines or geometric shapes—to suggest motion and digital growth, such as upward floating icon elements or stylized data sparkles, without cluttering the image. Use moderate detail: clean crisp edges, clear color blocking, and slight shading, but avoid excessive complexity to maintain focus and infographic compatibility. Absolutely no text, words, letters, or written content anywhere in the image—express the concept entirely through the arrangement, color, and form of the visual elements. The image should enhance the infographic, providing clear thematic representation of app download growth for both iOS and Google with a technology-driven, forward-moving feel, while ensuring the all-white background remains untouched for high contrast and seamless integration.'}, 'pictogram_1.png': {'pictogram_prompt': 'Create a professionally designed, visually engaging illustration for an infographic titled "App Downloads Growth: iOS vs Google", using a clean, pure white background. Focus on a modern technology theme, with a minimalist flat vector art style. Visually represent the concept of rising app downloads by depicting two distinct upward growth metaphors: on the left, an abstract stack of iOS app icons (symbolized by rounded squares with a prominent blue corner, using [28, 144, 248] and [37, 86, 169]) rising in staggered heights like a digital bar graph or tower; on the right, a matching stack of Google Play symbols (rectangles or triangles with greenish and neutral tones, using [227, 216, 131], [197, 200, 200], and [18, 22, 24]), also arranged in an ascending pattern. Arrange both elements side-by-side, subtly suggesting comparison but without actual data bars or axes. Integrate small, clean geometric shapes, such as digital sparkles or upward arrows incorporated into the towers’ structure, to imply continuous growth and dynamic movement. Maintain a harmonious use of the required color palette—[227, 216, 131], [197, 200, 200], [28, 144, 248], [37, 86, 169], [18, 22, 24]—ensuring balanced contrast for a professional, cohesive look. The illustration should be moderately detailed, free of clutter, and designed to complement, not compete with, the data-driven content of the infographic. The image must contain absolutely no text, words, letters, or written content of any kind—communicate solely through visual elements for maximum clarity and integration with the infographic design.'}, 'pictogram_2.png': {'pictogram_prompt': 'Create a professionally designed, visually compelling illustration suitable for a modern infographic poster about "App Downloads Growth: iOS vs Google." The overall theme should emphasize technology and growth, with a focus on mobile app ecosystems. Use a clean minimalist vector style, with simple geometric shapes and smooth gradients for a modern, sophisticated look. The core concept to visualize is the competitive growth in app downloads between iOS (Apple) and Google (Android).\n\nDepict two large, stylized upward arrows or bar graphs side by side, each symbolizing one platform—one arrow prominently featuring a rounded, metallic circle suggestive of the iOS home button style, the other arrow topped with angular elements that subtly evoke the Google Play triangle (do not use trademarked icons or actual logos). Ensure the arrows or bars are visually distinct but balanced, rising dynamically to imply progress and competition.\n\nAround the arrows, integrate subtle abstract visual cues—such as floating app icon shapes, digital sparkles, or network nodes—to further reinforce the concept of digital growth and app ecosystems. Use harmonious arrangements and moderate detailing for visual clarity and engagement, avoiding clutter.\n\nThe entire illustration must be rendered on a pure white background. The color palette should mostly incorporate harmonious blends of the following RGB colors: [227, 216, 131] (a warm golden hue), [197, 200, 200] (light neutral grey), [28, 144, 248] (bright blue), [37, 86, 169] (deep blue), and [18, 22, 24] (dark neutral). These colors should be distributed thoughtfully among the elements for a balanced and visually appealing composition.\n\nMost importantly, the illustration must contain absolutely no text, words, letters, or any written content of any kind—purely communicate through visual forms and symbolic imagery only. Design the illustration to enhance and complement the infographic’s data, providing clear thematic context without overshadowing or distracting from the information presented.'}, 'pictogram_4.png': {'pictogram_prompt': 'Create a visually striking, professional illustration for an infographic poster titled "App Downloads Growth: iOS vs Google." The main visual theme should center on modern technology and dynamic digital growth, with a clean, minimalist flat vector style. Visually represent the competition and comparative growth between the iOS App Store and Google Play by depicting two upward-trending, stylized bar or column graphs positioned side by side. Each set of bars should subtly integrate iconographic elements: one side featuring a simplified, abstract smartphone symbol with rounded edges and a softly glowing apple-like silhouette (without using any actual brand icons), the other side displaying an angular device shape incorporating a geometric triangle motif reminiscent of the Google Play symbol (again, entirely abstract and not replicating any logo). \n\nBoth sets of bars should rise at a distinct angle, visually reflecting growth, with the peaks subtly highlighted using the provided RGB colors. Balance and interlace the color palette of [227, 216, 131], [197, 200, 200], [28, 144, 248], [37, 86, 169], and [18, 22, 24] throughout both groups to create contrast and visual harmony, with accent colors on the bars and device shapes, and more neutral colors on secondary or background elements. \n\nAt the base of the graphs, add clean, abstract dotted or dashed lines rising alongside the bars, suggesting data flow and digital momentum. Optionally, introduce minimalist geometric shapes—such as circles or arrows in the palette’s colors—to subtly emphasize upward motion and progress, ensuring the composition feels dynamic but uncluttered.\n\nUse a pure white background for the entire illustration to ensure perfect integration with an infographic layout, maximizing clarity and contrast. The illustration should be highly clean, moderately detailed, and visually engaging—without overwhelming the viewer or competing with the infographic’s core data presentation. \n\nAbsolutely no text, letters, numbers, or any form of written content should appear in the illustration—visual communication only. All elements should be carefully composed to enhance and complement the infographic’s focus on app downloads growth for iOS vs Google, providing thematic relevance and an inviting, technology-focused atmosphere suitable for modern infographic design.'}, 'pictogram_0.png': {'pictogram_prompt': 'Create a professional, visually engaging illustration for an infographic titled "App Downloads Growth: iOS vs Google." The main theme should be modern technology, focusing on the concept of app growth and competition between iOS and Google platforms. Use a clean, minimalist flat vector style with geometric elements for clarity and sophistication. \n\nThe central composition should feature two stylized, abstract smartphone icons side by side—one subtly referencing iOS (rounded corners, lighter palette) and the other referencing Google/Android (slightly sharper corners, darker palette)—without using any logos, actual app icons, or text of any kind. Depict upward movement to symbolize growth by integrating a series of ascending bar or arrow-like shapes emerging from each phone. These growth shapes should differ subtly in design or placement for each platform, visually suggesting a comparison of app download trends without implying a winner. \n\nIncorporate harmonious, balanced use of the specified color palette: soft gold (RGB 227, 216, 131), light gray (RGB 197, 200, 200), bright blue (RGB 28, 144, 248), deep blue (RGB 37, 86, 169), and very dark gray (RGB 18, 22, 24). Distribute these colors among the phones, growth shapes, and minimal accent details for contrast, ensuring good visual hierarchy and cohesion. \n\nEnsure all elements, including the phones and growth shapes, are moderately detailed with clean lines and modern shading, but avoid unnecessary complexity. Use abstract, data-inspired visual cues rather than literal representations. The illustration must not contain any text, words, letters, or written symbols—imagery only. The background must be pure white, maximizing contrast and allowing easy integration into an infographic layout. The overall visual should feel balanced, professional, and enhance the infographic’s message without overpowering the data display.'}}
        print("generation_status['pictogram_options']:",generation_status['pictogram_options'])

        # 生成配图
        generation_status['progress'] = '绘制配图中...'
        for pictogram_option in generation_status['pictogram_options']:
            thread = Thread(target=generator.generate_image, 
                            args=(generation_status['pictogram_options'][pictogram_option]["pictogram_prompt"],
                                "pictogram",
                                f'buffer/{generation_status["id"]}/{pictogram_option}'))
            thread.start()
        
        
        
        # print("title_options:", generation_status['title_options'])
        generation_status['status'] = 'completed'
        generation_status['completed'] = True

    except Exception as e:
        generation_status['status'] = 'error'
        generation_status['progress'] = str(e)
        generation_status['completed'] = True
        print(f"title_generation 出错 {e} {traceback.format_exc()}")
    


# def simulate_final_generation(image_name):
#     global generation_status
    
#     steps = [
#         ('生成图表...', 1.5),
#         ('按照模板进行元素布局...', 2),
#         ('完成！', 0)
#     ]
    
#     generation_status['step'] = 'final_generation'
#     generation_status['status'] = 'processing'
#     generation_status['completed'] = False
    
#     for step, duration in steps:
#         generation_status['progress'] = step
#         time.sleep(duration)
    
#     generation_status['step'] = 'final_result'
#     generation_status['status'] = 'completed'
#     generation_status['completed'] = True
#     generation_status['image_name'] = image_name


# thread = Thread(target=generate_variation, args=("processed_data/App.json", 
#                                                          f"buffer/20251118080418_1491/d3-js/multiple pie chart/multiple_pie_chart_02.svg", 
#                                                          [
#         "d3-js/multiple pie chart/multiple_pie_chart_02",
#         [
#           "x",
#           "y",
#           "group"
#         ]
#       ],
#     [
#       [
#         227,
#         216,
#         131
#       ],
#       [
#         197,
#         200,
#         200
#       ],
#       [
#         28,
#         144,
#         248
#       ],
#       [
#         37,
#         86,
#         169
#       ],
#       [
#         18,
#         22,
#         24
#       ]
#     ],
#     [
#       245,
#       243,
#       239
#     ],))
# thread.start()