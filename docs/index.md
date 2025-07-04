# DermAlert Backend

![DermAlert Logo](https://www.dermalert.ai/land/dist/logo-dermalert.png)

Bem-vindo à documentação do **DermAlert Backend** - um sistema backend robusto para diagnóstico dermatológico assistido por IA.

## 🎯 Sobre o Projeto

O DermAlert é uma plataforma que utiliza inteligência artificial para auxiliar no diagnóstico de condições dermatológicas, proporcionando:

- **Análise de imagens** dermatológicas com IA
- **Gestão de pacientes** e histórico médico
- **Sistema de consultas** online e presenciais
- **Catálogos médicos** completos (doenças, medicamentos, alergias)
- **Integração com unidades de saúde**

## 🏗️ Arquitetura

O projeto é construído com:

- **Django REST Framework** - API robusta e escalável
- **PostgreSQL** - Banco de dados principal
- **MinIO** - Armazenamento de objetos (imagens)
- **Docker** - Containerização para desenvolvimento e produção
- **uv** - Gerenciamento de dependências Python moderno

## 📚 Guias Rápidos

### Primeiros Passos
1. [Configuração do PostgreSQL](setup/postgres.md)
2. [Ambiente de Desenvolvimento](setup/development.md)
3. [Guia Rápido de Seeds](seeds/quick-guide.md)

### Para Desenvolvedores
- [Arquitetura do Sistema](development/architecture.md)
- [Executar Testes](development/testing.md)
- [Referência da API](api/accounts.md)

## 🚀 Início Rápido

```bash
# 1. Clonar o repositório
git clone https://github.com/DermAlert/dermalert-backend
cd dermalert-backend

# 2. Subir serviços - Terminal 1
make dev

# 3. Configurar banco de dados - Terminal 2
make setup-db

# 4. Popular com dados de teste - Terminal 2
make seed
```

## 🛠️ Comandos Principais

| Comando | Descrição |
|---------|-----------|
| `make dev` | Subir ambiente de desenvolvimento |
| `make setup-db` | Configurar banco de dados |
| `make seed` | Popular com dados de teste |
| `make test` | Executar testes |
| `make shell` | Django shell |

## 📖 Estrutura da Documentação

- **[Configuração](setup/postgres.md)** - Setup do ambiente
- **[Seeds](seeds/quick-guide.md)** - Sistema de dados de teste
- **[API](api/accounts.md)** - Documentação das APIs
- **[Desenvolvimento](development/architecture.md)** - Guias para desenvolvedores

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
