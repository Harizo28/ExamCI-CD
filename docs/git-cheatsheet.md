# Git Cheat Sheet

## Configuration (une fois par machine)
```bash
git config --global user.name "Ton Nom"
git config --global user.email "ton.email@example.com"
git config --global init.defaultBranch main
```

## Init & Clone
| Commande | Rôle |
|----------|------|
| `git init` | Initialiser un dépôt local |
| `git clone <url>` | Cloner un dépôt GitHub |

## Workflow quotidien
| Commande | Rôle |
|----------|------|
| `git status` | Voir l'état des fichiers |
| `git add <fichier>` | Stager un fichier |
| `git add .` | Stager tout (respecte .gitignore) |
| `git commit -m "msg"` | Enregistrer les changements stagés |
| `git push` | Envoyer sur GitHub |
| `git pull` | Récupérer depuis GitHub |

## Branches
| Commande | Rôle |
|----------|------|
| `git branch` | Lister les branches |
| `git switch -c <nom>` | Créer + basculer sur une branche |
| `git switch <nom>` | Basculer sur une branche existante |
| `git merge <branche>` | Fusionner une branche dans la courante |
| `git branch -d <nom>` | Supprimer une branche (safe) |

## Historique
| Commande | Rôle |
|----------|------|
| `git log --oneline` | Historique compact |
| `git log --graph --all` | Vue globale avec branches |
| `git diff` | Voir les changements non stagés |
| `git show <hash>` | Détails d'un commit |

## Remote
| Commande | Rôle |
|----------|------|
| `git remote add origin <url>` | Lier GitHub |
| `git remote -v` | Lister les remotes |
| `git push -u origin main` | Premier push |

## Annuler
| Commande | Rôle |
|----------|------|
| `git restore <fichier>` | Annuler modifs non stagées |
| `git restore --staged <fic>` | Retirer du stage |
| `git reset --soft HEAD~1` | Annuler dernier commit (garde les changements) |
| `git revert <hash>` | Créer un commit inverse (safe pour code pushé) |

## Convention de messages
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `test:` tests
- `ci:` pipeline CI/CD
- `refactor:` refactorisation
- `chore:` tâches diverses
