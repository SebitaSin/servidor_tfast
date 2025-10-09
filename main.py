import os
from fastapi import FastAPI, Body

app = FastAPI(title="Servidor T-FAST", version="0.1")

@app.get("/salud")
def salud():
    return {"ok": True, "mensaje": "Servidor funcionando"}

# --- reglas ANGELS mínimas ---
@app.post("/v1/angels/validar")
def validar(datos: dict = Body(...)):
    errores, avisos = [], []
    sbp = datos.get("sbp")
    dbp = datos.get("dbp")
    glu = datos.get("glu")
    tac_ok = datos.get("tac_sin_hemorragia")

    if sbp is None or dbp is None:
        errores.append("Falta TA inicial (SBP/DBP)")
    if glu is None:
        errores.append("Falta glucemia")
    if tac_ok is not True:
        errores.append("TAC sin hemorragia no confirmada")

    return {"errors": errores, "warnings": avisos, "can_proceed": len(errores) == 0}

# --- cálculo dosis rt-PA / TNK ---
@app.post("/v1/dosis")
def dosis(datos: dict = Body(...)):
    agente = (datos.get("agente") or "rtPA").lower()
    peso = float(datos.get("peso_kg") or 0)
    if peso <= 0:
        return {"error": "Peso inválido"}

    if agente == "rtpa":
        total = min(0.9 * peso, 90.0)
        bolo = round(total * 0.10, 2)
        infusion = round(total - bolo, 2)
        return {"agente": "rtPA", "total_mg": round(total,2), "bolo_mg": bolo, "infusion_mg": infusion}
    else:
        total = min(0.25 * peso, 25.0)
        return {"agente": "TNK", "total_mg": round(total,2)}

# Para Replit/Render/Railway: usar el puerto del entorno
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
