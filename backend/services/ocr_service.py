import cv2
import warnings  #warnings ha stop panna
import easyocr
import os
import numpy as np

os.environ['EASYOCR_LOGGING']='False' #used to remove the GPU message
warnings.filterwarnings("ignore",category=UserWarning)
reader = easyocr.Reader(['en'], gpu=False, verbose=False)

def calculate_weight(roi):
    """Calculates font weight based on pixel density."""
    if roi.size == 0: return 0
    # Threshold to binary (Black & White)
    _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Calculate percentage of black pixels (text ink)
    weight_score = (np.sum(binary == 255) / binary.size) * 100
    return round(weight_score, 2)

def preprocess_for_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    return clahe.apply(gray)

def extract_text_from_image(image_path):
    try:
        if not os.path.exists(image_path): return []
        img = cv2.imread(image_path)
        processed = preprocess_for_ocr(img)
        
        # Single Stream Extraction
        results = reader.readtext(processed, contrast_ths=0.1, low_text=0.3)
        
        raw_data = []
        for (bbox, text, prob) in results:
            if prob > 0.20:
                clean_text = text.strip().upper()
                
                # Coordinates
                x_min, y_min = int(bbox[0][0]), int(bbox[0][1])
                x_max, y_max = int(bbox[2][0]), int(bbox[2][1])
                
                # Height = Font Size
                h = y_max - y_min
                
                # Extract the specific text area to check Weight
                # We use a small padding to ensure we get the whole letter
                roi = processed[max(0, y_min):y_max, max(0, x_min):x_max]
                weight = calculate_weight(roi)
                
                raw_data.append({
                    "text": clean_text,
                    "height": h,
                    "weight": weight, # Higher weight = Bolder text
                    "top": y_min,
                    "left": x_min
                })

        if not raw_data: return []
        
        # Return grouped text
        return group_by_font_style(raw_data)
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return []

def group_by_font_style(data):
    # Sort by Y-coordinate first
    data.sort(key=lambda x: (x['top'], x['left']))
    merged = []
    if not data: return []
    
    current_group = [data[0]]
    for i in range(1, len(data)):
        prev, curr = current_group[-1], data[i]
        
        # Logic: If on the same line AND having similar Font Size/Weight
        if abs(curr['top'] - prev['top']) < 15 and abs(curr['height'] - prev['height']) < 10:
            current_group.append(curr)
        else:
            merged.append(merge_block(current_group))
            current_group = [curr]
            
    merged.append(merge_block(current_group))
    return merged

def merge_block(group):
    group.sort(key=lambda x: x['left'])
    return {
        "text": " ".join([item['text'] for item in group]),
        "height": sum([item['height'] for item in group]) // len(group),
        "weight": sum([item['weight'] for item in group]) // len(group),
        "top": min([item['top'] for item in group])
    }