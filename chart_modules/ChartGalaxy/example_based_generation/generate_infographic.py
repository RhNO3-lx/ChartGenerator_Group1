import os
import pandas as pd
import openai
import requests
from pathlib import Path
import time
import json
from typing import List, Dict, Optional
from PIL import Image
import base64
import numpy as np
import cv2
from io import BytesIO
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(str(Path(__file__).parent))

API_KEY = "sk-ug32KbbvEDPucqnaB207A5EcEd6f47Dc887c14249a12Ff43"
BASE_URL = "https://aihubmix.com/v1"

style_options = [
    "minimalist flat design",
    "soft pastel vector style",
    "modern geometric illustration",
    "isometric semi-realistic style",
    "conceptual abstract imagery",
    "retro-inspired muted vector art",
    "futuristic holographic-style vector",
    "clean professional vector design"
]

subject_options = [
    "abstract geometric shapes",
    "organic flowing curves",
    "interconnected network nodes",
    "symbolic human silhouettes (no facial features)",
    "stylized natural elements",
    "data-inspired 3D blocks",
    "layered conceptual shapes",
    "minimalistic object icons",
    "symbolic spherical representations",
    "abstract landscape forms",
    "dynamic arrow-like motion elements"
]

class InfographicImageGenerator:
    def __init__(self):
        """
        Initialize image generator
        
        Args:
            api_key: OpenAI API key
            base_url: Optional API base URL for custom endpoint
        """
        self.client = openai.OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        self.processed_data_dir = "processed_data"
        self.output_dir = "generated_images"
        self.prompts_dir = "."
        
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/titles", exist_ok=True)
        os.makedirs(f"{self.output_dir}/pictograms", exist_ok=True)
        # Coming Soon directories
        os.makedirs(f"{self.output_dir}/chart_variations", exist_ok=True)
        os.makedirs(f"{self.output_dir}/final_infographics", exist_ok=True)
        
    def load_prompt_file(self, filename: str) -> str:
        """Load prompt file content"""
        prompt_path = os.path.join(str(Path(__file__).parent), filename)

        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
        
    
    def read_csv_data(self, csv_path: str) -> str:
        """Read CSV file and convert to string format"""
        try:
            df = pd.read_csv(csv_path)
            # Convert CSV data to string format, including column names and first few rows of data
            csv_content = f"Columns: {', '.join(df.columns.tolist())}\n"
            csv_content += f"Data shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
            csv_content += "Sample data:\n"
            csv_content += df.head(10).to_string(index=False)
            return csv_content
        except Exception as e:
            print(f"Failed to read CSV file {csv_path}: {e}")
            return ""
    
    def generate_title_text(self, csv_data: str) -> str:
        """Generate title text using GPT-4"""
        try:
            # Load title recommendation prompt
            title_prompt_template = self.load_prompt_file("generate_title_recommendation_prompt.md")
            if not title_prompt_template:
                return "Data Analysis Report"
            
            # Replace CSV data placeholder
            prompt = title_prompt_template.replace("{csv_data}", csv_data)
            
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            title = response.choices[0].message.content.strip()
            print(f"Generated title: {title}")
            return title
            
        except Exception as e:
            print(f"Failed to generate title text: {e}")
            return "Data Insights"
    
    def generate_image_prompt(self, title: str, prompt_type: str, color=None) -> str:
        """Generate image generation prompt"""
        try:
            if prompt_type == "title":
                # Read title prompt file and use GPT-4.1 to generate professional image prompt
                title_prompt_template = self.load_prompt_file("generate_title_image_prompt.md")
                title_prompt = title_prompt_template.replace("{title}", title).replace("{color}", f"{color}")
                
                response = self.client.chat.completions.create(
                    model="gpt-image-1",
                    messages=[
                        {"role": "user", "content": title_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                prompt = response.choices[0].message.content.strip()
                print(f"Generated title image prompt: {prompt}...")
                
            elif prompt_type == "pictogram":
                # Read pictogram prompt file and use GPT-4.1 to generate professional image prompt
                pictogram_prompt_template = self.load_prompt_file("generate_pictogram_prompt.md")
                
                style_choice = random.choice(style_options)
                subject_choice = random.choice(subject_options)
                pictogram_prompt = pictogram_prompt_template.replace("{title}", title).replace("{color}", f"{color}").replace("{style_choice}", f"{style_choice}").replace("{subject_choice}", f"{subject_choice}")
                
                response = self.client.chat.completions.create(
                    model="gpt-image-1",
                    messages=[
                        {"role": "user", "content": pictogram_prompt}
                    ],
                )
                prompt = response.choices[0].message.content.strip()
                print(f"Generated pictogram image prompt: {prompt}...")
            
            return prompt
            
        except Exception as e:
            print(f"Failed to generate image prompt: {e}")
            return f"Create a simple {prompt_type} image about {title}"
    
    def generate_image(self, prompt: str, image_type: str, filename: str) -> bool:
        """Generate image using GPT-Image-1"""
        try:
            print(f"Generating {image_type} image: {filename}")

            response = self.client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="high",
            )

            if response and response.data:
                image_base64 = response.data[0].b64_json
                image_data = base64.b64decode(image_base64)
                image= Image.open(BytesIO(image_data))
                # Convert to RGBA mode
                image = image.convert('RGBA')
                data = image.getdata()

                # Convert white (tolerance 20) to transparent
                new_data = []
                for item in data:
                    # Check if RGB value is close to white (tolerance 20)
                    if item[0] > 235 and item[1] > 235 and item[2] > 235:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)

                image.putdata(new_data)

                # Convert image to numpy array
                img_array = np.array(image)

                # Create binary mask, non-transparent pixels are 1, transparent pixels are 0
                mask = (img_array[:,:,3] > 0).astype(np.uint8)

                # Mark connected regions
                num_labels, labels = cv2.connectedComponents(mask)

                # Calculate number of pixels in each connected region
                for label in range(1, num_labels):
                    area = np.sum(labels == label)
                    # If region pixel count is less than 20, set it to transparent
                    if area < 20:
                        img_array[labels == label] = [255, 255, 255, 0]

                # Convert back to PIL image
                image = Image.fromarray(img_array)

                os.makedirs(os.path.dirname(filename), exist_ok=True)
                image.save(filename)
                print(f"Image saved: {filename}")
                return True

            else:
                print(f"Failed to generate image: {response.status_code}")
                return False

        except Exception as e:
            print(f"Failed to generate image: {e}")
            return False

    def generate_title_image(self, title_text: str, reference_image_path: str, output_filename: str) -> bool:
        """
        Generate title image using Gemini model with reference image style

        Args:
            title_text: The title text to generate image for
            reference_image_path: Path to the reference chart image for style
            output_filename: Path to save the generated image

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Generating title image for: {title_text}")

            # Read and encode reference image
            with open(reference_image_path, 'rb') as img_file:
                reference_image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            # Determine image mime type
            if reference_image_path.lower().endswith('.png'):
                mime_type = "image/png"
            elif reference_image_path.lower().endswith('.jpg') or reference_image_path.lower().endswith('.jpeg'):
                mime_type = "image/jpeg"
            elif reference_image_path.lower().endswith('.svg'):
                # SVG needs special handling - convert to PNG first or use as text
                mime_type = "image/svg+xml"
            else:
                mime_type = "image/png"

            # Create prompt for Gemini
            prompt = f"""参考这个图表的视觉风格（颜色搭配、字体风格），生成一个**纯标题文字图片**。

标题内容："{title_text}"

严格要求：
1. **只生成标题文字**，禁止生成任何图表、数据、图形、图标或其他元素
2. 标题文字必须清晰可读，使用与参考图表相似的字体风格和颜色
3. 背景必须是透明
4. 图片比例为宽扁形（宽高比约为 4:1 或 5:1），适合作为信息图表的横幅标题
5. 文字居中排列，可以是单行或两行
6. 不要添加任何装饰性图案、边框或阴影

输出：一张简洁的标题文字图片，仅包含"{title_text}"这几个字"""

            # Call Gemini API
            response = self.client.chat.completions.create(
                model="gemini-3-pro-image-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{reference_image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    },
                ],
                modalities=["text", "image"],
                temperature=0.7,
            )

            # Process response
            if (
                hasattr(response.choices[0].message, "multi_mod_content")
                and response.choices[0].message.multi_mod_content is not None
            ):
                for part in response.choices[0].message.multi_mod_content:
                    if "inline_data" in part and part["inline_data"] is not None:
                        print("🖼️ Title image content received")
                        image_data = base64.b64decode(part["inline_data"]["data"])
                        image = Image.open(BytesIO(image_data))

                        # Convert to RGBA for transparency
                        image = image.convert('RGBA')

                        # Process white background to transparent
                        data = image.getdata()
                        new_data = []
                        for item in data:
                            if item[0] > 235 and item[1] > 235 and item[2] > 235:
                                new_data.append((255, 255, 255, 0))
                            else:
                                new_data.append(item)
                        image.putdata(new_data)

                        # Save image
                        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
                        image.save(output_filename)
                        print(f"✅ Title image saved to: {output_filename}")
                        return True

            print("No valid image response received from Gemini")
            return False

        except Exception as e:
            print(f"Failed to generate title image: {e}")
            return False
    
    def process_csv_file(self, csv_file: str):
        """Process a single CSV file"""
        print(f"\nProcessing CSV file: {csv_file}")
        
        # Read CSV data
        csv_path = os.path.join(self.processed_data_dir, csv_file)
        csv_data = self.read_csv_data(csv_path)
        
        if not csv_data:
            print(f"Skipping file {csv_file} - read failed")
            return
        
        base_filename = os.path.splitext(csv_file)[0]
        
        # Generate 4 images
        for i in range(1):
            print(f"\nGenerating {i+1} set of images...")

            # Generate title text
            title_text = self.generate_title_text(csv_data)
        
            # Generate title image
            title_prompt = self.generate_image_prompt(title_text, "title")
            title_filename = f"{self.output_dir}/titles/{base_filename}_title_{i}.png"
            
            print(title_prompt)
            success = self.generate_image(title_prompt, "title", title_filename)
            if success:
                # Add delay to avoid API limits
                time.sleep(1)
            
            # Generate pictogram image
            pictogram_prompt = self.generate_image_prompt(title_text, "pictogram")
            pictogram_filename = f"{self.output_dir}/pictograms/{base_filename}_pictogram_{i+1}.png"
            
            success = self.generate_image(pictogram_prompt, "pictogram", pictogram_filename)
            if success:
                # Add delay to avoid API limits
                time.sleep(2)
            
            # Coming Soon: generate chart variations and use layout template
    
    def process_all_csv_files(self):
        """Process all CSV files"""
        if not os.path.exists(self.processed_data_dir):
            print(f"Error: Cannot find directory {self.processed_data_dir}")
            return
        
        csv_files = [f for f in os.listdir(self.processed_data_dir) if f.endswith('.csv')]
        
        if not csv_files:
            print(f"No CSV files found in {self.processed_data_dir}")
            return
        
        print(f"Found {len(csv_files)} CSV files")
        
        for csv_file in csv_files:
            try:
                self.process_csv_file(csv_file)
            except Exception as e:
                print(f"Error processing file {csv_file}: {e}")
                continue
    
    def generate_title_option(self, csv_path: str, reference_image_path: str, output_dir: str = None):
        """
        Generate title options in parallel

        Args:
            csv_path: Path to the CSV data file
            reference_image_path: Path to the reference chart image for style
            output_dir: Directory to save generated title images (optional)

        Returns:
            Dict with title options including text and image paths
        """
        title_options = {}
        csv_data = self.read_csv_data(csv_path)

        if output_dir is None:
            output_dir = f"{self.output_dir}/titles"

        def generate_single_title(i):
            # Step 1: Generate title text from CSV data using LLM
            title_text = self.generate_title_text(csv_data)

            # Step 2: Generate title image using Gemini with reference image style
            output_filename = os.path.join(output_dir, f"title_{i}.png")
            success = self.generate_title_image(title_text, reference_image_path, output_filename)

            return f"title_{i}.png", {
                'title_text': title_text,
                'image_path': output_filename if success else None,
                'success': success
            }

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_single_title, i) for i in range(5)]
            for future in as_completed(futures):
                key, value = future.result()
                title_options[key] = value

        return title_options

    def generate_single_title(self, csv_path: str, reference_image_path: str, output_filename: str):
        """
        Generate a single title image

        Args:
            csv_path: Path to the CSV data file
            reference_image_path: Path to the reference chart image for style
            output_filename: Path to save the generated title image

        Returns:
            Dict with title text and image path
        """
        csv_data = self.read_csv_data(csv_path)

        # Step 1: Generate title text from CSV data using LLM
        title_text = self.generate_title_text(csv_data)

        # Step 2: Generate title image using Gemini with reference image style
        success = self.generate_title_image(title_text, reference_image_path, output_filename)

        return {
            'title_text': title_text,
            'image_path': output_filename if success else None,
            'success': success
        }

    def generate_single_pictogram(self, title_text: str, colors, output_filename: str):
        """
        Generate a single pictogram image

        Args:
            title_text: The title text for context
            colors: Color palette to use
            output_filename: Path to save the generated pictogram image

        Returns:
            Dict with pictogram prompt and success status
        """
        # Generate pictogram prompt
        pictogram_prompt = self.generate_image_prompt(title_text, "pictogram", colors)

        # Generate the pictogram image
        success = self.generate_image(pictogram_prompt, "pictogram", output_filename)

        return {
            'pictogram_prompt': pictogram_prompt,
            'image_path': output_filename if success else None,
            'success': success
        }

    def generate_pictogram_option(self, title_text, colors):
        """Generate pictogram options"""
        pictogram_options = {}

        def generate_single_pictogram(i):
            pictogram_prompt = self.generate_image_prompt(title_text, "pictogram", colors)
            return f"pictogram_{i}.png", {"pictogram_prompt": pictogram_prompt}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_single_pictogram, i) for i in range(5)]
            for future in as_completed(futures):
                key, value = future.result()
                pictogram_options[key] = value

        return pictogram_options

def main():
    """Main function"""
    print("=== Infographic Generator ===")
    
    # Create generator and start processing
    generator = InfographicImageGenerator()
    generator.process_all_csv_files()
    
    print("\n=== Processing completed ===")
    print(f"Generated images saved in: {generator.output_dir}")

if __name__ == "__main__":
    main() 
