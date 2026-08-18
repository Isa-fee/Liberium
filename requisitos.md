# LEVANTAMENTO DE REQUISITOS DO LUMINA

## 1. INTRODUÇÃO

O presente documento tem como objetivo apresentar o levantamento de requisitos do sistema **Lumina**, um sistema de gerenciamento de dados para bibliotecas. O sistema visa facilitar o controle de livros, usuários, empréstimos e devoluções, proporcionando uma solução eficiente e organizada.

## 2. DESCRIÇÃO GERAL DO SISTEMA

O sistema **Lumina** será uma aplicação web que permitirá o gerenciamento completo de uma biblioteca. Entre suas principais funcionalidades estão o cadastro e controle de livros, autenticação de usuários e gerenciamento de empréstimos.

O sistema será desenvolvido utilizando tecnologias modernas, incluindo **HTML, CSS e Vue.js** no frontend, além de uma **API REST** no backend.

## 3. REQUISITOS FUNCIONAIS

Os requisitos funcionais descrevem as funcionalidades que o sistema deve oferecer.

## 3.1 Gerenciamento de Usuários

### RF01 – Cadastro de Usuários

**RF01.01** – O sistema deve permitir o cadastro de novos usuários mediante o preenchimento dos seguintes dados obrigatórios:

- Nome completo;
- E-mail;
- Senha;
- Confirmação de senha.

**RF01.02** – O sistema deve validar se o endereço de e-mail informado já está cadastrado.

**RF01.03** – O sistema não deve permitir o cadastro de usuários com e-mails duplicados.

**RF01.04** – O sistema deve validar se a senha possui no mínimo 8 caracteres.

**RF01.05** – O sistema deve exibir mensagem de erro caso a senha e a confirmação de senha sejam diferentes.

**RF01.06** – O sistema deve armazenar os dados do usuário após a validação das informações fornecidas.

### RF02 – Login de Usuários

**RF02.01** – O sistema deve permitir que usuários cadastrados realizem login utilizando e-mail e senha.

**RF02.02** – O sistema deve validar as credenciais informadas antes de conceder acesso.

**RF02.03** – O sistema deve exibir mensagem de erro quando o e-mail ou a senha forem inválidos.

**RF02.04** – O sistema deve direcionar o usuário autenticado para a página principal da aplicação.

### RF03 – Autenticação JWT

**RF03.01** – O sistema deve gerar um token JWT após a autenticação bem-sucedida do usuário.

**RF03.02** – O sistema deve utilizar o token JWT para validar o acesso às rotas protegidas.

**RF03.03** – O sistema deve impedir o acesso a recursos protegidos quando o token for inválido ou expirado.

### RF04 – Logout de Usuários

**RF04.01** – O sistema deve permitir que o usuário encerre sua sessão a qualquer momento.

**RF04.02** – O sistema deve invalidar o token JWT após o logout.

**RF04.03** – O sistema deve redirecionar o usuário para a tela de login após o encerramento da sessão.

## 3.2 Gerenciamento de Livros

### RF05 – Cadastro de Livros

**RF05.01** – O sistema deve permitir o cadastro de livros contendo os seguintes dados:

- Título;
- Autor;
- Categoria;
- ISBN;
- Quantidade disponível.

**RF05.02** – O sistema deve validar o preenchimento dos campos obrigatórios.

**RF05.03** – O sistema não deve permitir o cadastro de livros sem título, autor ou categoria.

**RF05.04** – O sistema não deve permitir o cadastro de livros com ISBN já registrado.

**RF05.05** – O sistema deve armazenar as informações do livro após a validação dos dados.

### RF06 – Consulta de Livros

**RF06.01** – O sistema deve permitir a visualização da lista de livros cadastrados.

**RF06.02** – O sistema deve exibir informações detalhadas de cada livro.

**RF06.03** – O sistema deve apresentar a disponibilidade atual de cada exemplar.

### RF07 – Edição de Livros

**RF07.01** – O sistema deve permitir a atualização das informações de livros cadastrados.

**RF07.02** – O sistema deve validar os dados informados antes de salvar as alterações.

**RF07.03** – O sistema deve registrar as alterações realizadas no cadastro do livro.

### RF08 – Exclusão de Livros

**RF08.01** – O sistema deve permitir a exclusão de livros cadastrados.

**RF08.02** – O sistema não deve permitir a exclusão de livros que possuam empréstimos ativos.

**RF08.03** – O sistema deve solicitar confirmação antes da exclusão definitiva do livro.

### RF09 – Busca de Livros

**RF09.01** – O sistema deve permitir a busca de livros por título.

**RF09.02** – O sistema deve permitir a busca de livros por autor.

**RF09.03** – O sistema deve permitir a busca de livros por categoria.

**RF09.04** – O sistema deve exibir apenas os resultados compatíveis com os filtros informados.

## 3.3 Gerenciamento de Empréstimos

### RF10 – Registro de Empréstimos

**RF10.01** – O sistema deve permitir registrar empréstimos associando um usuário a um livro disponível.

**RF10.02** – O sistema deve verificar a disponibilidade do livro antes de concluir o empréstimo.

**RF10.03** – O sistema deve registrar automaticamente a data do empréstimo.

**RF10.04** – O sistema deve associar o empréstimo ao usuário responsável.

### RF11 – Registro da Data de Empréstimo

**RF11.01** – O sistema deve armazenar automaticamente a data de empréstimo.

**RF11.02** – A data registrada deve corresponder ao momento da confirmação do empréstimo.

### RF12 – Definição de Prazo de Devolução

**RF12.01** – O sistema deve calcular automaticamente a data prevista de devolução.

**RF12.02** – O prazo padrão de devolução deve ser de 15 dias corridos após a data do empréstimo.

**RF12.03** – O sistema deve exibir ao usuário a data prevista para devolução.

### RF13 – Registro de Devoluções

**RF13.01** – O sistema deve permitir registrar a devolução de livros emprestados.

**RF13.02** – O sistema deve atualizar automaticamente a disponibilidade do exemplar devolvido.

**RF13.03** – O sistema deve registrar a data efetiva da devolução.

### RF14 – Controle de Disponibilidade

**RF14.01** – O sistema não deve permitir empréstimos de livros indisponíveis.

**RF14.02** – O sistema deve exibir mensagem de erro quando um livro não estiver disponível para empréstimo.

### RF15 – Consulta de Empréstimos

**RF15.01** – O sistema deve permitir listar todos os empréstimos cadastrados.

**RF15.02** – O sistema deve exibir informações sobre usuário, livro, data de empréstimo e prazo de devolução.

**RF15.03** – O sistema deve permitir filtrar empréstimos por usuário ou situação.

## 3.4 Controle de Atrasos

### RF16 – Identificação de Empréstimos em Atraso

**RF16.01** – O sistema deve identificar automaticamente empréstimos cuja data prevista de devolução seja anterior à data atual.

**RF16.02** – O sistema deve atualizar o status do empréstimo para "Em atraso".

**RF16.03** – O sistema deve destacar visualmente os empréstimos em atraso.

### RF17 – Consulta de Empréstimos em Atraso

**RF17.01** – O sistema deve permitir a visualização de todos os empréstimos em atraso.

**RF17.02** – O sistema deve exibir informações sobre o usuário responsável e o período de atraso.

**RF17.03** – O sistema deve permitir filtrar apenas empréstimos com status "Em atraso".

## 4. REQUISITOS NÃO FUNCIONAIS

Os requisitos não funcionais descrevem as características de qualidade e restrições do sistema.

## 4.1 Segurança

### RNF01 – Autenticação

O sistema deve utilizar autenticação baseada em JWT para controle de acesso.

### RNF02 – Proteção de Rotas

O sistema deve restringir o acesso às rotas privadas apenas para usuários autenticados.

### RNF03 – Armazenamento de Senhas

As senhas dos usuários devem ser armazenadas utilizando algoritmos de hash criptográfico seguros.

## 4.2 Arquitetura

### RNF04 – API REST

A aplicação deve seguir os princípios de arquitetura REST para comunicação entre cliente e servidor.

### RNF05 – Stateless

A API deve ser stateless, não armazenando estado da sessão no servidor.

## 4.3 Interface

### RNF06 – Interface Web

O sistema deve possuir interface web desenvolvida utilizando HTML, CSS e Vue.js.

### RNF07 – Responsividade

A interface deve adaptar-se adequadamente a dispositivos desktop, tablet e smartphone.

### RNF08 – Usabilidade

A interface deve apresentar navegação intuitiva e consistente para facilitar o uso por diferentes perfis de usuários.

## 4.4 Desempenho

### RNF09 – Tempo de Resposta

O sistema deve responder às operações de consulta em até 2 segundos em condições normais de uso.

### RNF10 – Concorrência

O sistema deve suportar múltiplos usuários simultâneos sem degradação significativa de desempenho.

## 4.5 Infraestrutura

### RNF11 – Containerização

A aplicação deve ser executada em containers Docker.

### RNF12 – Compatibilidade

A aplicação deve ser compatível com ambientes Podman.

### RNF13 – Orquestração

A aplicação deve ser implantável em ambiente Kubernetes.

### RNF14 – Infraestrutura como Código

A infraestrutura necessária para implantação deve ser definida utilizando ferramentas de Infrastructure as Code (IaC).

## 4.6 Qualidade

### RNF15 – Testes

O sistema deve possuir testes automatizados para validação das funcionalidades críticas antes da entrega.

### RNF16 – Documentação

O sistema deve possuir documentação técnica contendo instruções de instalação, configuração, execução e utilização da API.

### RNF17 – Manutenibilidade

O código-fonte deve seguir padrões de organização e boas práticas de desenvolvimento para facilitar manutenção e evolução do sistema.

### RNF18 – Versionamento

O código-fonte deve ser versionado utilizando Git e armazenado em repositório remoto compartilhado pela equipe.
