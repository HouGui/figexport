TEX_HEADER = r"""
\documentclass{standalone}

\usepackage{tikz}
\usepackage{pgf-pie}
"""

# Remove the leading newline
TEX_HEADER = TEX_HEADER.lstrip('\n')

TEX_BEGIN_DOCUMENT = r"""
\begin{document}

"""

TEX_END_DOCUMENT = r"""
\end{document}
"""

TEX_COLORS = r"""
\definecolor{green_dark}{RGB}{0,150,130}
\definecolor{green_mid}{RGB}{97,181,167}
\definecolor{green_light}{RGB}{155,217,197}
\definecolor{green_very_light}{RGB}{229,244,242}

\definecolor{blue_dark}{RGB}{70, 100, 170}
\definecolor{blue_mid}{RGB}{125,146,195}
\definecolor{blue_light}{RGB}{222,235,247}

\definecolor{orange_mid}{RGB}{241,151,173}
\definecolor{orange_light}{RGB}{248,203,173}

\definecolor{gray_very_dark}{RGB}{50,50,50}
\definecolor{gray_dark}{RGB}{102,102,102}
\definecolor{gray_mid}{RGB}{197,197,197}
\definecolor{gray_light}{RGB}{236,236,236}

\definecolor{keyword}{RGB}{70,100,170}
\definecolor{my_brown}{RGB}{194,101,23}
"""
