# from biblioteche-fantasma root

cd report

# update relazione.tex

pdflatex relazione.tex
biber relazione
pdflatex relazione.tex
pdflatex relazione.tex

# github commit
cd ..

git status
git add -u report
git diff --cached
git commit -m "Updated final report"
git push origin main