# dalla root biblioteche-fantasma

cd report

# modifica relazione.tex

pdflatex relazione.tex
biber relazione
pdflatex relazione.tex
pdflatex relazione.tex

cd ..

git status
git add -u report
git diff --cached
git commit -m "Updated final report"
git push origin main