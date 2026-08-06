# yt-dlp GUI - Instalador para macOS

## 📌 Para o seu chefe

Isso funciona em **qualquer Mac com Python 3 instalado**.

### ⚡ Quick Start (SUPER simples)

1. **Abra Terminal** (Cmd + Space, type "terminal")
2. **Navegue para a pasta do projeto:**
   ```bash
   cd /path/to/ytdlp-gui
   ```
3. **Primeira vez - Verificar requisitos:**
   ```bash
   chmod +x *.sh && bash check_and_setup_mac.sh
   ```
   - Vai perguntar o que instalar (y/n)
   - Você decide

4. **Depois - Compilar:**
   ```bash
   bash build_installer_mac.sh
   ```
   - Espera terminar ☕

✅ **Pronto!** Você terá seu DMG em `dist/`

### ✅ Quando terminar:

- Um arquivo chamado `ytdlp-gui-1.0.0.dmg` estará em `dist/`
- Esse é o **instalador pronto para distribuir**
- Qualquer pessoa pode:
  1. Baixar o `.dmg`
  2. Duplo-clique pra abrir
  3. Arrastar o app para Applications
  4. Pronto! Instalado

---

## 🔧 O que faz o script:

- ✅ Instala dependências Python
- ✅ Gera um ícone para o app
- ✅ Compila a app com PyInstaller
- ✅ Cria um DMG instalável profissional

---

## 📖 Mais detalhes:

Ver `BUILD_DMG_MAC.txt` para troubleshooting e instruções detalhadas.

---

## 📍 Resultado final:

```
dist/
└── ytdlp-gui-1.0.0.dmg  ← Distribuir isso!
```

Pronto pra enviar pro seu time! 🚀
