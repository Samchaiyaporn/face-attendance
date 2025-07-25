import sys
import os
import traceback

try:
    print('   → Importing InsightFace...')
    import insightface
    print('   ✅ InsightFace imported successfully')

    print('   → Loading buffalo_l model...')
    app = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])

    print('   → Preparing model with optimization...')
    app.prepare(ctx_id=0, det_size=(640, 640))

    print('   ✅ Face Recognition Models พร้อมใช้งาน')

    # ตรวจสอบ model directory
    model_dir = os.path.join(os.path.expanduser('~'), '.insightface', 'models')
    if os.path.exists(model_dir):
        model_files = os.listdir(model_dir)
        print(f'   → Models directory: {model_dir}')
        print(f'   → Model files: {len(model_files)} files')

except ImportError as e:
    print(f'   ❌ Import Error: {e}')
    print('   กรุณาติดตั้ง: pip install insightface onnxruntime')
    sys.exit(1)

except Exception as e:
    print(f'   ❌ Model preparation failed: {e}')
    traceback.print_exc()
    sys.exit(1)
