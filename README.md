# Do LLMs Get More Lost in Bangla?

A CSE 6701 Advanced Artificial Intelligence research project at the Military Institute of Science and Technology. The study asks whether splitting the same math problem across chat turns hurts LLM accuracy more in Bangla than in English.

The proposed experiment uses matched English and Bangla problems from MGSM-Rev2. It compares accuracy when the problem segments arrive together versus one per turn, then tests whether repeating earlier segments improves accuracy. This repository contains the study design and poster.

## Materials

- [Research proposal (PDF)](Proposal_LostInBangla_Public.pdf), [LaTeX source](proposal-public.tex), and [shared figures](figs.tex)
- [A4 poster (PDF)](Poster_Group2_LostInBangla_A4.pdf) and [LaTeX source](poster.tex)
- [Upstream study code and data](https://github.com/microsoft/lost_in_conversation)

To build the proposal and poster, run the following from the repository root with a TeX distribution that includes TikZ.

```sh
pdflatex proposal-public.tex
pdflatex poster.tex
```

## License

The original project materials are licensed under [Creative Commons Attribution 4.0 International](LICENSE). Credit Anika Ashraf, Faria Alam, Faysal Ahmed, Abrar Mahir Esam, Sachitra Halder, and Muntasir Hasan Porag.
