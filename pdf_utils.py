import os
try:
    import PyMuPDF as fitz  # Try importing the newer package name first
except ImportError:
    try:
        import fitz  # Try the traditional import
    except ImportError:
        print("Error: PyMuPDF package not found. Please install it using:")
        print("pip install PyMuPDF")
        raise
from PIL import Image
import io
import shutil

def convert_pdf_to_images(pdf_path, output_dir=None, dpi=300, format='png'):
    """
    将PDF文件转换为图像并保存到指定目录。
    
    Args:
        pdf_path (str): PDF文件的路径
        output_dir (str, optional): 图像保存的目录路径，默认为 imgs/pdf文件名
        dpi (int, optional): 图像的分辨率，默认为300
        format (str, optional): 图像格式，默认为png
        
    Returns:
        list: 包含所有生成图像路径的列表
    """
    # 检查输入文件是否存在
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    # 获取PDF文件名（不含路径和扩展名）
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 如果未指定输出目录，则使用默认目录
    if output_dir is None:
        # 基于文件名创建目录 imgs/pdf文件名
        output_dir = os.path.join("imgs", pdf_filename)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    # 初始化图像路径列表
    image_paths = []
    
    # 遍历PDF的每一页
    for page_number in range(len(pdf_document)):
        # 获取页面
        page = pdf_document.load_page(page_number)
        
        # 将页面渲染为图像，计算合适的分辨率
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), alpha=False)
        
        # 设置图像文件名
        image_filename = f"{pdf_filename}_page_{page_number+1}.{format}"
        image_path = os.path.join(output_dir, image_filename)
        
        # 将图像保存到文件
        pix.save(image_path)
        
        # 添加图像路径到返回列表
        image_paths.append(image_path)
        
        print(f"已保存第 {page_number+1} 页: {image_path}")
    
    # 关闭PDF文档
    pdf_document.close()
    
    print(f"已将PDF文件 '{pdf_path}' 转换为 {len(image_paths)} 张图像，保存在 '{output_dir}'")
    
    return image_paths

def batch_convert_pdfs(pdf_dir, output_base_dir="imgs", dpi=300, format='png'):
    """
    批量转换目录中的所有PDF文件为图像
    
    Args:
        pdf_dir (str): 包含PDF文件的目录
        output_base_dir (str): 图像输出的基础目录，默认为 imgs
        dpi (int): 图像的分辨率
        format (str): 图像格式
    
    Returns:
        dict: PDF文件名到图像路径列表的映射
    """
    # 确保输出基础目录存在
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 初始化结果字典
    results = {}
    
    # 遍历目录中的文件
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            pdf_name = os.path.splitext(filename)[0]
            
            # 为每个PDF创建专用输出目录
            output_dir = os.path.join(output_base_dir, pdf_name)
            
            # 转换PDF并获取图像路径
            image_paths = convert_pdf_to_images(pdf_path, output_dir, dpi, format)
            
            # 存储结果
            results[pdf_name] = image_paths
    
    return results

def cleanup_temp_images(pdf_name=None, base_dir="imgs"):
    """
    清理为PDF生成的临时图像文件
    
    Args:
        pdf_name (str, optional): PDF文件名（不含扩展名），如果提供则只清理该PDF对应的图像
        base_dir (str): 图像所在的基础目录
    """
    if pdf_name:
        # 清理特定PDF的图像
        pdf_dir = os.path.join(base_dir, pdf_name)
        if os.path.exists(pdf_dir):
            shutil.rmtree(pdf_dir)
            print(f"已删除图像目录: {pdf_dir}")
    else:
        # 清理基础目录中的所有PDF图像目录
        if os.path.exists(base_dir):
            for dir_name in os.listdir(base_dir):
                dir_path = os.path.join(base_dir, dir_name)
                if os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)
            print(f"已清理所有PDF图像目录")

if __name__ == "__main__":
    # 测试示例
    pdf_path = "example.pdf"  # 替换为实际PDF路径
    if os.path.exists(pdf_path):
        image_paths = convert_pdf_to_images(pdf_path)
        print(f"生成的图像路径: {image_paths}")
    else:
        print(f"示例文件 {pdf_path} 不存在，请提供有效的PDF路径进行测试")
