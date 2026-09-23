import os
# Eliminate OpenMP/MKL busy-waiting loops to drastically drop idle CPU usage
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["KMP_BLOCKTIME"] = "0"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import sys
import uvicorn

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import HOST, PORT

if __name__ == "__main__":
    print("=" * 65)
    print("   🅿️  INICIANDO SISTEMA INTELIGENTE DE MONITOREO DE PARQUEADERO")
    print(f"   🚀  Servidor web listo en: http://localhost:{PORT}")
    print("=" * 65)
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False, workers=1)
