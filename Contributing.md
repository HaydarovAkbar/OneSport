# Contributing Guidelines

Welcome! To ensure a smooth development process and high code quality, please follow these guidelines when contributing to this project.

---

## 1. Code Commit and Branching Rules

- **Commit Frequently**: Make small, frequent commits to keep a detailed history of changes.
- **Work only on your task**: Don't work on the tasks that are not assigned to you on Asana
- **Write Meaningful Commit Messages**: Use clear, descriptive messages. For example, `Fix bug in user login` instead of `Fixed stuff`.
- **Use Feature Branches**: Create a new branch for each feature, bug fix, or task. Follow naming conventions:
  - `feature/feature-name` for new features
  - `bugfix/bug-name` for bug fixes
  - `chore/chore-name` for maintenance
- **Do Not Merge Your Own Pull Requests**: All pull requests must be reviewed and approved by another developer to maintain code quality.
- **Suggestions are welcome**: If you have suggestions to improve the structure or code, please present them. Start working on it only if the changes are approved. 
- **Keep Pull Requests Small**: Limit each pull request to a single feature or bug fix to make reviews easier and faster.
- **Review Other PRs**: Actively participate in reviewing others’ pull requests to encourage teamwork and shared ownership.


---

## 2. Coding Standards and Style

- **No Tabs - 4 Spaces for Indentation**: Use 4 spaces for indentation, not tabs. In your IDE, set tabs to 8 spaces so that any accidental tab usage is visually noticeable and can be corrected.
- **Follow Established Code Style**: Use consistent naming conventions, indentation, and spacing. Linters and formatters (e.g., ESLint, Prettier) help enforce code style automatically.
- **Write Clean, Readable Code**: Use meaningful names for variables and functions. Prioritize readability and maintainability over clever shortcuts.
- **Use Comments Judiciously**: Comment only when necessary to explain complex logic. Clear, self-explanatory code is preferred.
- **Avoid Nested If statements**: Avoid if statement within if statement whereever possible. three levels is just prohibited.
- **Write small functions**: A function should do one thing, not many. Do not wirte functions that are longer than absolutely neccessary.  


---

## 3. API related

Use HTTP methods according to their intended purpose to maintain a clear and consistent API design:
- `GET`: Retrieve data.
- `POST`: Create new resources.
- `PUT` or `PATCH`: Update existing resources.
- `DELETE`: Remove resources.

- **Use Plural Nouns for Endpoints**: Resource names should be plural to indicate collections. For example, use `/users` instead of `/user`.

- **Avoid Verbs in Endpoints**: Actions are represented by HTTP methods, not verbs in the URL. For instance, use `POST /users` instead of `/createUser`.

- **Nest Endpoints Logically**: Use nested routes to represent relationships between resources. For example, `/users/{user_id}/posts` can represent posts that belong to a user.

- **Consistent Response Structure**: For predictable and readable responses, follow a standard structure. Include status messages, error codes, and data as separate objects. Here’s an example:

```json
{
  "status": "success",
  "data": { "user": { "id": 1, "name": "John Doe" } }
}
```
---

Thank you for following these guidelines! Your adherence ensures a high standard of code quality and a smooth workflow for everyone.
