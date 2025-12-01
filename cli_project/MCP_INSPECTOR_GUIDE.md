# Guia do MCP Inspector

## Como conectar ao MCP Server usando o Inspector

### Opção 1: Usando `mcp dev` (Recomendado - mais simples)

Este método já está funcionando! Basta executar no terminal:

```bash
cd cli_project
mcp dev mcp_server.py
```

O MCP Inspector abrirá automaticamente no navegador e se conectará ao servidor.

**Se o botão "Connect" não funciona:**
- Recarregue a página do navegador (F5)
- Ou clique em "Back to Connect" e tente novamente

### Opção 2: Configuração Manual no Inspector

Se você quiser configurar manualmente, use estas configurações:

#### Com UV:
- **Transport Type**: STDIO
- **Command**: `uv`
- **Arguments**: `run mcp_server.py`

#### Sem UV (Python direto):
- **Transport Type**: STDIO
- **Command**: `python`
- **Arguments**: `mcp_server.py`

**IMPORTANTE**: NÃO use `mcp run` nos argumentos quando estiver usando o Inspector. O `mcp run` é apenas para executar via linha de comando diretamente.

### Opção 3: Testar o servidor via linha de comando

Para testar se o servidor está funcionando sem o Inspector:

```bash
# Com UV
uv run --with mcp mcp run mcp_server.py

# Sem UV
python -m mcp run mcp_server.py
```

Isso iniciará o servidor em modo STDIO e você poderá testar enviando mensagens JSON diretamente.

## Verificando que está funcionando

Quando conectado com sucesso, você deverá ver:

1. **Tools** disponíveis:
   - `read_document` - Lê o conteúdo de um documento
   - `edit_document` - Edita o conteúdo de um documento

2. **Resources** (quando implementados - atualmente em TODO):
   - Lista de IDs de documentos
   - Conteúdo de documentos específicos

3. **Prompts** (quando implementados - atualmente em TODO):
   - Reescrever documento em markdown
   - Resumir documento

## Testando as Tools

Uma vez conectado, você pode testar as tools no Inspector:

### Testar read_document:
```json
{
  "doc_id": "deposition.md"
}
```

### Testar edit_document:
```json
{
  "doc_id": "deposition.md",
  "old_str": "Angela Smith",
  "new_str": "Angela M. Smith"
}
```

## Problemas Comuns

### "Nothing happens when clicking Connect"
- **Solução**: Use `mcp dev mcp_server.py` em vez de configurar manualmente
- Ou recarregue a página e tente novamente

### "Server not responding"
- Verifique se você está no diretório correto (`cli_project`)
- Certifique-se de que o arquivo `mcp_server.py` existe
- Execute `python test_basic.py` para validar o ambiente

### "Authentication required"
- O MCP Inspector gera um token de autenticação
- Ele já está incluído na URL automaticamente quando você usa `mcp dev`
- Se necessário, você pode desabilitar com a variável de ambiente: `DANGEROUSLY_OMIT_AUTH=true`

## Próximos Passos

Depois de conectar com sucesso:

1. Teste as ferramentas existentes (`read_document`, `edit_document`)
2. Implemente os TODOs no `mcp_server.py`:
   - Adicione resources para listar documentos
   - Adicione prompts para resumir/reformatar documentos
3. Veja os resultados em tempo real no Inspector
