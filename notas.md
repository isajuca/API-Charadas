## ENDPOINTS PÚBLICOS (Open)
- **GET** - /charadas - (Todas as charadas )
- **GET** - /charadas/{id} - (Charada específica)
- **GET** - /charadas/aleatoria - (Charada aleatória)

## ENDPOINTS PRIVADOS (Autenticação Bearer)
- **POST** - /charadas - (Criar charada)
- **PATCH** - /charadas/<int:id> - (Alterar parcialmente pelo id)
- **PUT** - /charadas/<int:id> - (Alterar inteiramente pelo id )
- **DELETE** - /charadas/<int:id> - (Deletar charada pelo id)

## TECNOLOGIAS
- Database: Firebase Firestore da Google (NO-SQL - Não relacional)
- HOST: vercel