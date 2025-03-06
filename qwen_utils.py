import json
import random
import io
import ast
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageColor
from IPython.display import Markdown, display
from openai import OpenAI
import os
import base64
from qwen_vl_utils import smart_resize
import re
import sys

# Constants
min_pixels = 512*28*28
max_pixels = 2048*28*28
prompt = "Spotting all the sentence in the image with line-level. Avoid word-by-word output. And output in JSON format."
image_path = "./imgs/ppt.png"

# Get API key from environment variable
MODELSCOPE_API_KEY = os.getenv("MODELSCOPE_API_KEY")

# Check if API key is available
if not MODELSCOPE_API_KEY:
    print("Warning: MODELSCOPE_API_KEY environment variable not set!")
    print("Please set it using:")
    print("  export MODELSCOPE_API_KEY='your-api-key'  # on Linux/macOS")
    print("  set MODELSCOPE_API_KEY=your-api-key  # on Windows")

def parse_json(json_output):
    """
    解析 JSON 输出字符串，去除 markdown 格式化标记。
    Args:
        json_output (str): 包含 markdown 格式的 JSON 字符串。
    Returns:
        str: 解析后的 JSON 字符串。
    """
    # 解析 markdown 格式
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(lines[i+1:])  # 移除 "```json" 之前的所有内容
            json_output = json_output.split("```")[0]  # 移除结尾 "```" 之后的所有内容
            break  # 找到 "```json" 后退出循环
    return json_output

def translateWithAPI(raw:str):
    '''
    通过API翻译文本
    Args:
        raw (str): 需要翻译的文本。
    Returns:
        str: 翻译后的文本。
    '''
    # Check if API key is available
    if not MODELSCOPE_API_KEY:
        print("Error: MODELSCOPE_API_KEY not set. Cannot perform translation.")
        return raw  # Return original text if no API key
        
    client = OpenAI(
        base_url='https://api-inference.modelscope.cn/v1/',
        api_key=MODELSCOPE_API_KEY,  # Use environment variable
    )

    response = client.chat.completions.create(
        model='Qwen/Qwen2.5-7B-Instruct',  # ModelScope Model-Id
        messages=[
            {
                'role': 'system',
                'content': '请将以下中文句子翻译成英文，输出只需包含翻译结果。'
            },
            {
                'role': 'user',
                'content': raw
            }
        ],
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def get_font(size=40):
    font_paths = [
        "/System/Library/Fonts/SF-Pro.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNSText.ttf"
    ]
    
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    
    # Fallback to default
    return ImageFont.truetype(size=size)

def plot_text_bounding_boxes(image_path, response, input_width, input_height):
    """
    在图像上绘制带有名称标记的边界框，使用 PIL 库、归一化坐标和不同颜色。

    Args:
        image_path (str): 图像文件的路径。
        response (str): 包含对象名称及其位置的边界框列表，这是一个JSON格式的字符串。
        input_width: 模型输入的图像宽度
        input_height: 模型输入的图像高度
        
    Returns:
        PIL.Image: 修改后的图像对象
    """

    # 加载图像
    img = Image.open(image_path)
    width, height = img.size
    print(img.size)
    # 创建绘图对象
    draw = ImageDraw.Draw(img)

    # 解析 markdown 格式的JSON (修复变量名不一致的问题)
    try:
        json_data = parse_json(response)
        
        try:
             font = ImageFont.truetype("/Library/Fonts/NotoSansCJK-Regular.ttc", size=50)  # 典型安装路径
        except OSError:
            # 如果字体文件不存在，使用默认字体
            font = get_font(size=40)
            print("未找到 NotoSansCJK 字体，使用默认字体。")
        
        # 尝试解析JSON数据
        try:
            # 尝试修复常见的JSON格式问题
            if isinstance(json_data, str):
                # 修复 ":=" 问题
                json_data = json_data.replace(':=', ':')
                
                # 使用json模块尝试解析
                try:
                    parsed_boxes = json.loads(json_data)
                except json.JSONDecodeError:
                    # 如果还是失败，尝试使用正则表达式提取有效信息
                    pattern = r'"bbox_2d":\s*\[(.*?)\],\s*"text_content":\s*"(.*?)"'
                    matches = re.findall(pattern, json_data)
                    
                    parsed_boxes = []
                    for match in matches:
                        coords = [int(x.strip()) for x in match[0].split(',')]
                        text = match[1]
                        parsed_boxes.append({
                            "bbox_2d": coords,
                            "text_content": text
                        })
            else:
                parsed_boxes = json_data
        except Exception as e:
            print(f"JSON解析失败: {e}")
            print("尝试使用ast.literal_eval...")
            # 尝试使用ast.literal_eval作为备选方案
            try:
                parsed_boxes = ast.literal_eval(json_data)
            except:
                print(f"无法解析JSON数据: {json_data[:200]}...")
                return img  # 返回原图
                
        # 处理解析后的边界框
        for i, bounding_box in enumerate(parsed_boxes):
            color = 'red'

            # 检查bbox_2d是否存在且格式正确
            if "bbox_2d" not in bounding_box or not isinstance(bounding_box["bbox_2d"], list) or len(bounding_box["bbox_2d"]) < 4:
                print(f"跳过无效边界框: {bounding_box}")
                continue

            # 将归一化坐标转换为绝对坐标
            abs_y1 = int(bounding_box["bbox_2d"][1]/input_height * height)
            abs_x1 = int(bounding_box["bbox_2d"][0]/input_width * width)
            abs_y2 = int(bounding_box["bbox_2d"][3]/input_height * height)
            abs_x2 = int(bounding_box["bbox_2d"][2]/input_width * width)

            if abs_x1 > abs_x2:
                abs_x1, abs_x2 = abs_x2, abs_x1

            if abs_y1 > abs_y2:
                abs_y1, abs_y2 = abs_y2, abs_y1

            # 绘制边界框
            draw.rectangle(
                ((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=1
            )

            # 绘制文本
            if "text_content" in bounding_box and bounding_box["text_content"]:
                try:
                    translated_text = translateWithAPI(bounding_box["text_content"])
                    draw.text((abs_x1, abs_y2), translated_text, fill=color, font=font, align="center")
                except Exception as e:
                    print(f"翻译或绘制文本时出错: {e}")
                    draw.text((abs_x1, abs_y2), bounding_box["text_content"], fill=color, font=font, align="center")
    
    except Exception as e:
        print(f"处理边界框数据时出错: {e}")
        print(f"原始响应数据: {response[:200]}...")  # 只打印前200个字符避免日志过长
        # 返回原始图像，不进行处理
    
    # 返回修改后的图像
    return img

def save_image(image, output_path):
    """
    保存图像到指定路径。

    Args:
        image (PIL.Image): 要保存的图像对象。
        output_path (str): 保存图像的路径。
    
    Returns:
        str: 保存图像的完整路径。
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # 保存图像
    image.save(output_path)
    print(f"图像已保存到: {output_path}")
    
    return output_path

def encode_image(image_path):
    """
    将图像编码为 Base64 字符串。

    Args:
        image_path (str): 要编码的图像的路径。

    Returns:
        str: 图像的 Base64 编码字符串。
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def inference_with_api(image_path, prompt, sys_prompt="You are a helpful assistant.", model_id="Qwen/Qwen2.5-VL-7B-Instruct", min_pixels=512*28*28, max_pixels=2048*28*28):
    """
    使用 API 进行图像推理。

    Args:
        image_path (str): 图像文件的路径。
        prompt (str): 用户输入的提示文本。
        sys_prompt (str, optional): 系统提示文本。默认为 "You are a helpful assistant."。
        model_id (str): 模型名称
        min_pixels: 最小像素
        max_pixels: 最大像素

    Returns:
        str:  API 返回的生成文本。
    """
    # Check if API key is available
    if not MODELSCOPE_API_KEY:
        raise ValueError("MODELSCOPE_API_KEY environment variable not set. Cannot perform inference.")
        
    # 检验image_path由什么后缀结尾
    if not image_path.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise ValueError("image_path must end with .png, .jpg, .jpeg, or .webp")
    
    # 读取image_path的图片
    base64_image = encode_image(image_path)
    # 提取出image_path的后缀
    image_ext = os.path.splitext(image_path)[1]
    if image_ext == '.webp':
        url = f"data:image/webp;base64,{base64_image}"
    elif image_ext == '.jpeg' or image_ext == '.jpg':
        url = f"data:image/jpeg;base64,{base64_image}"
    elif image_ext == '.png':
        url = f"data:image/png;base64,{base64_image}"

    client = OpenAI(
        api_key=MODELSCOPE_API_KEY,  # Use environment variable
        base_url="https://api-inference.modelscope.cn/v1/",
    )
    
    messages=[
        {
            "role": "system",
            "content": [{"type":"text","text": sys_prompt}]},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "min_pixels": min_pixels,
                    "max_pixels": max_pixels,
                    "image_url": {"url": url },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    completion = client.chat.completions.create(
        model = model_id,
        messages = messages,
    )
    return completion.choices[0].message.content

# Use an API-based approach to inference.
def main(image_path, output_path=None, pdf_name=None):
    """
    主函数，处理图像并保存结果。
    
    Args:
        image_path (str): 输入图像的路径。
        output_path (str, optional): 输出图像的路径。如果未提供，将基于输入生成。
        pdf_name (str, optional): PDF文件名，用于组织输出目录结构。
    
    Returns:
        str: 保存图像的路径。
    """
    try:
        image = Image.open(image_path)
        width, height = image.size

        input_height, input_width = smart_resize(height, width, min_pixels=min_pixels, max_pixels=max_pixels)
        
        print(f"处理图像: {image_path}")
        response = inference_with_api(image_path, prompt, min_pixels=min_pixels, max_pixels=max_pixels)
        
        display(Markdown(response))
        
        # 获取修改后的图像
        modified_image = plot_text_bounding_boxes(image_path, response, input_width, input_height)
        
        # 如果未提供输出路径，则基于输入路径生成
        if output_path is None:
            file_name = os.path.basename(image_path)
            base_name, ext = os.path.splitext(file_name)
            
            # 如果提供了PDF名称，将输出组织在对应子目录下
            if pdf_name:
                output_dir = os.path.join("outputs", pdf_name)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{base_name}_translated{ext}")
            else:
                output_path = os.path.join(os.path.dirname(image_path), f"{base_name}_translated{ext}")
        
        # 保存图像
        return save_image(modified_image, output_path)
    except Exception as e:
        print(f"处理图像时出错: {e}")
        import traceback
        traceback.print_exc()
        
        # 如果发生错误，创建一个空白图像并保存
        if output_path is None:
            file_name = os.path.basename(image_path)
            base_name, ext = os.path.splitext(file_name)
            
            if pdf_name:
                output_dir = os.path.join("outputs", pdf_name)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{base_name}_translated{ext}")
            else:
                output_path = os.path.join(os.path.dirname(image_path), f"{base_name}_translated{ext}")
        
        # 复制原图作为输出
        shutil.copy(image_path, output_path)
        print(f"由于错误，已复制原图到: {output_path}")
        return output_path

import os
import re
from pdf_generator import natural_sort_key

def batch_process_images(image_paths, pdf_name=None, output_dir="outputs"):
    """
    批量处理图像并返回输出路径列表。
    
    Args:
        image_paths (list): 要处理的图像路径列表
        pdf_name (str, optional): PDF文件名，用于组织输出
        output_dir (str): 输出基础目录
        
    Returns:
        list: 处理后图像的路径列表
    """
    translated_paths = []
    
    # 如果提供了pdf_name，将输出组织在对应子目录下
    if pdf_name:
        output_dir = os.path.join(output_dir, pdf_name)
        os.makedirs(output_dir, exist_ok=True)
    
    # Sort input images using natural sort for predictable processing order
    image_paths = sorted(image_paths, key=natural_sort_key)
    
    # Process each image
    for image_path in image_paths:
        output_path = main(image_path, pdf_name=pdf_name)
        translated_paths.append(output_path)
    
    # Sort output paths as well to ensure they're in the right order
    translated_paths = sorted(translated_paths, key=natural_sort_key)
    return translated_paths

if __name__ == "__main__":
    # 运行主函数
    main(image_path)





