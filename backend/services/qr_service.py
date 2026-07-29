import cv2
def extract_qr_data(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None: return None

        detector = cv2.QRCodeDetector()

        # 1. Image Scaling (Most important for small QRs in posters)
        # Image-ai perusaakuna dhaan pixels clear-ah kidaikkum
        height, width = img.shape[:2]
        img = cv2.resize(img, (width*2, height*2), interpolation=cv2.INTER_LANCZOS4)

        # 2. Multiple Attempts (Preprocessing variations)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Method A: Original Gray
        data, _, _ = detector.detectAndDecode(gray)
        if data: return data

        # Method B: Contrast Enhancement (CLAHE)
        # Background dark-ah irundhu QR white-ah irundha idhu help pannum
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        data, _, _ = detector.detectAndDecode(enhanced)
        if data: return data

        # Method C: Morphological Operations (Closing)
        # QR code-la chinna gaps irundha adhai fill pannum
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        closed = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        data, _, _ = detector.detectAndDecode(closed)
        if data: return data

        return None
    except Exception as e:
        print(f"QR Fix Error: {e}")
        return None

