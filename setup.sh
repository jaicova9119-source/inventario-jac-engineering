mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"proyectos@jacengineering.com.co\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

---

### **1.3 Crear `runtime.txt`**

**Ubicación:** `C:\Proyectos\inventory-system\runtime.txt`

**CREA este archivo:**
```
python-3.11.7