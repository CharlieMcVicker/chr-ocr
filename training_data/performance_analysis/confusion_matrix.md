# Character-Level OCR Confusion Matrix Report

This report provides analysis of character-level substitution, deletion, and insertion errors to identify which Cherokee syllables/characters the fine-tuned model frequently confuses.

## Overall Statistics
- **Total Characters in Ground Truth**: 29470
- **Total Matches (Correct)**: 28683 (97.33% accuracy)
- **Total Substitutions**: 381 (1.29% substitution rate)
- **Total Deletions**: 406 (1.38% deletion rate)
- **Total Insertions**: 195 (0.66% insertion rate)

## Top 30 Confused Character Pairs (Substitutions)
| Truth | Predicted | Count | Context / Potential Reason |
| :---: | :-------: | :---: | :------------------------- |
| `4` | `Ꮞ` | 61 | |
| `?` | `Ꭾ` | 40 | |
| `Ꮐ` | `Ꮳ` | 9 | |
| `Ꭺ` | `Ꮩ` | 7 | |
| `Ꮛ` | `Ꭶ` | 7 | |
| `Ꭴ` | `Ꮕ` | 6 | |
| `Ꮌ` | `Ᏹ` | 5 | |
| `Ꮊ` | `Ꮎ` | 4 | |
| `Ꮐ` | `Ꮹ` | 4 | |
| `Ꮥ` | `Ꭶ` | 4 | |
| `4` | `1` | 3 | |
| `[` | `Ꭵ` | 3 | |
| `Ꭽ` | `Ꮞ` | 3 | |
| `Ꮊ` | `Ꮧ` | 3 | |
| `Ꮈ` | `Ꮔ` | 3 | |
| `.` | `-` | 3 | |
| `Ꮒ` | `Ᏺ` | 3 | |
| `Ꮵ` | `Ꮟ` | 3 | |
| `Ꮨ` | `Ꮧ` | 2 | |
| `Ꮘ` | `Ꮱ` | 2 | |
| `Ꭴ` | `Ꮳ` | 2 | |
| `Ꮕ` | `Ꭴ` | 2 | |
| `:` | `;` | 2 | |
| `0` | `Ꮎ` | 2 | |
| `Ꮣ` | `Ꮩ` | 2 | |
| `Ꮫ` | `-` | 2 | |
| `Ꮓ` | `Ꮑ` | 2 | |
| `Ꮴ` | `Ꭲ` | 2 | |
| `Ꮊ` | `Ꭴ` | 2 | |
| `Ꮈ` | `Ꮑ` | 2 | |

## Top 15 Deleted Characters
| Character | Deletion Count | Total in GT | Deletion Rate |
| :-------: | :------------: | :---------: | :------------: |
| ` ` | 53 | 4632 | 1.14% |
| `]` | 20 | 22 | 90.91% |
| `Ꭴ` | 18 | 774 | 2.33% |
| `Ꭽ` | 18 | 271 | 6.64% |
| `Ꮝ` | 17 | 1568 | 1.08% |
| `-` | 16 | 527 | 3.04% |
| `[` | 16 | 22 | 72.73% |
| `Ꮒ` | 10 | 765 | 1.31% |
| `Ꭲ` | 10 | 958 | 1.04% |
| `Ꭼ` | 10 | 411 | 2.43% |
| `Ꮕ` | 10 | 565 | 1.77% |
| `Ꮧ` | 10 | 1096 | 0.91% |
| `.` | 9 | 352 | 2.56% |
| `Ꮣ` | 9 | 602 | 1.50% |
| `,` | 8 | 572 | 1.40% |

## Top 15 Inserted Characters
| Character | Insertion Count |
| :-------: | :-------------: |
| ` ` | 35 |
| `-` | 15 |
| `Ꭰ` | 11 |
| `Ꭴ` | 7 |
| `Ꮎ` | 6 |
| `Ꮭ` | 6 |
| `2` | 5 |
| `Ꮖ` | 5 |
| `Ꮒ` | 4 |
| `Ꮢ` | 4 |
| `Ꮩ` | 4 |
| `Ꭽ` | 3 |
| `Ꮪ` | 3 |
| `Ᏼ` | 3 |
| `Ꭶ` | 3 |

