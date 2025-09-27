#!/usr/bin/env bash
# merge_branches.sh
# Скрипт для безопасного слияния побочных веток в main
# Использует squash и обновление README из main при конфликте
# Подходит для веток с CV-2-04 или другими изменениями

# Проверка аргументов
if [ $# -lt 1 ]; then
    echo "Usage: $0 <feature-branch> [--update-readme]"
    exit 1
fi

MAIN_BRANCH="main"
FEATURE_BRANCH=$1
UPDATE_README=${2:-}

echo "Слияние ветки '$FEATURE_BRANCH' в '$MAIN_BRANCH'"

# Переключаемся на main и обновляем
git checkout $MAIN_BRANCH || exit 1
git pull origin $MAIN_BRANCH

# Выполняем squash merge
git merge --squash $FEATURE_BRANCH
echo "Squash merge выполнен. Проверьте изменения."

# Разрешаем конфликты README.md — приоритет main
if [ -f README.md ]; then
    echo "Конфликт README.md — приоритет версии из '$MAIN_BRANCH'"
    git checkout --ours README.md
    git add README.md
fi

# Добавляем все остальные изменения автоматически
git add .

# Опционально: обновление README.md в исходной ветке
if [ "$UPDATE_README" == "--update-readme" ]; then
    echo "Обновление README.md в ветке '$FEATURE_BRANCH' из '$MAIN_BRANCH'"
    git checkout $FEATURE_BRANCH || exit 1
    git checkout $MAIN_BRANCH -- README.md
    git commit -m "Обновлён README.md из main"
    git checkout $MAIN_BRANCH
fi

echo
echo "Готово. Теперь можно зафиксировать объединённые изменения:"
echo "git commit -m 'Merge branch $FEATURE_BRANCH into $MAIN_BRANCH (squash)'"

