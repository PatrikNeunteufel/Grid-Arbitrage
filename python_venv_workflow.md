# Python venv Workflow (Kurz & korrekt)

## 1. Virtuelle Umgebung erstellen
```bash
python -m venv .venv
```

## 2. In venv aktivieren

### Windows (PowerShell)
```bash
.venv\Scripts\Activate.ps1
```

### Windows (CMD)
```bash
.venv\Scripts\activate.bat
```

### Linux / macOS
```bash
source .venv/bin/activate
```

## 3. pip aktualisieren
```bash
python -m pip install --upgrade pip
```

## 4. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

## 5. Aktuelle Umgebung einfrieren (für Reproduzierbarkeit)
```bash
pip freeze > requirements.txt
```

## 6. Optional: Pakete upgraden

Alle Pakete upgraden:
```bash
pip list --outdated
pip install --upgrade <paketname>
```

Oder gezielt:
```bash
pip install --upgrade requests
```

## 7. venv verlassen
```bash
deactivate
```

---

---

## 🔹 Hinweise zur Benennung der venv

- Der Name der Umgebung ist **frei wählbar**:
```bash
python -m venv .venv
python -m venv venv
python -m venv my_env
```

- Empfehlung: `.venv`
  - wird von vielen Tools (z. B. Visual Studio Code) automatisch erkannt
  - bleibt im Projektordner lokal
  - auf Linux/macOS „versteckt“ (beginnt mit `.`)

---

## 🔹 Vorhandene venvs finden

Python selbst führt **keine globale Liste** von virtuellen Umgebungen.

### Im aktuellen Projekt
```bash
ls      # Linux/macOS
dir     # Windows
```

### Aktive Umgebung prüfen
```bash
where python   # Windows
which python   # Linux/macOS
```

oder:
```bash
python -c "import sys; print(sys.prefix)"
```

### venvs rekursiv suchen
```bash
find . -type d -name ".venv"
```

---

## 🔹 Alternative Tools mit Environment-Management

- conda → `conda env list`
- virtualenvwrapper → `workon`
- poetry → automatische venv-Verwaltung

---

## Kurzablauf (TL;DR)
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

