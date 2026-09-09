# Data Story - Biblioteche Fantasma

Lo snapshot ICCU contiene 19.611 record. Il primo risultato non è un conteggio di “biblioteche chiuse”, ma una tassonomia di condizioni: 13.200 record non hanno uno stato speciale registrato, 1.827 sono “non più esistenti”, 1.723 “non censiti”, 1.502 “confluiti”, 619 “temporaneamente chiusi” e pochi altri ricadono in inagibilità, sisma, riapertura parziale o deposito senza servizio. Questa distinzione evita di trasformare fenomeni amministrativi diversi in un'unica categoria.

Per l'analisi principale il progetto considera problematici 2.497 casi su 18.956 biblioteche, pari al 13,17%. Il fenomeno è nazionale ma diseguale: Molise e Liguria hanno le quote regionali più alte, mentre i maggiori numeri assoluti si concentrano nei sistemi con più biblioteche. Milano registra 139 casi, Roma 117 e Genova 90. Una quota elevata su una base piccola e un conteggio elevato su una base grande raccontano due aspetti diversi dello stesso fenomeno.

Il confronto con la demografia 2019-2025 introduce una domanda intuitiva: i comuni che perdono popolazione hanno più biblioteche problematiche? La risposta è più prudente di una narrazione lineare. Su 6.659 comuni comparabili con almeno una biblioteca, la correlazione è negativa ma debole: Pearson -0,106 e Spearman -0,067. I comuni in calo mostrano una quota media più alta, ma la dispersione è ampia e la mediana è zero in entrambi i gruppi. Lo spopolamento può essere un contesto, non una causa dimostrata da questi dati.

Il patrimonio mostra un secondo limite informativo. Solo 627 delle 2.497 biblioteche problematiche hanno righe patrimonio nel dataset secondario. Le quantità sono spesso disponibili, ma 461 righe sono missing. Per i fondi speciali, nessun record ricade nel perimetro problematico. Questo risultato non significa che i fondi non esistano: significa che lo snapshot secondario non li documenta per queste biblioteche.

Le confluenze raccontano invece la trasformazione istituzionale. Dei 1.502 record, 1.412 hanno un target ISIL validato. La rete risultante è frammentata in 410 componenti, con alcuni target che assorbono molti nodi. Non è quindi una “rete di chiusure”, ma una mappa di riorganizzazioni amministrative osservate nello snapshot.

Infine, i dati sono stati trasformati in un knowledge graph da 1.644.602 triple esplicite e collegati a risorse esterne con copertura quasi completa. L'interlinking raggiunge 100% per le biblioteche verso ICCU e 99,9620% per i comuni verso Linked ISPRA. Il progetto arriva tecnicamente al paradigma Linked Data, ma non dichiara una pubblicazione 5-star operativa: le URI locali usano `.invalid` e non sono dereferenziabili sul Web.

La storia complessiva è quindi una storia di **eterogeneità, copertura e cautela**: gli stati non sono equivalenti, la geografia conta ma va normalizzata per il denominatore, la demografia mostra soltanto un'associazione debole, i missing non sono zeri e la semantica deve essere precisa quanto le statistiche.
