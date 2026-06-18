# Character-Level OCR Confusion Matrix Report

This report provides analysis of character-level substitution, deletion, and insertion errors to identify which Cherokee syllables/characters the fine-tuned model frequently confuses.

## Overall Statistics
- **Total Characters in Ground Truth**: 29470
- **Total Matches (Correct)**: 26755 (90.79% accuracy)
- **Total Substitutions**: 2334 (7.92% substitution rate)
- **Total Deletions**: 381 (1.29% deletion rate)
- **Total Insertions**: 1490 (5.06% insertion rate)

## Top 30 Confused Character Pairs (Substitutions)
| Truth | Predicted | Count | Context / Potential Reason |
| :---: | :-------: | :---: | :------------------------- |
| `Ꮧ` | `Ꮨ` | 260 | |
| `Ꮣ` | `Ꮦ` | 108 | |
| `Ꮅ` | `Ꮭ` | 72 | |
| `,` | `;` | 62 | |
| `-` | `”` | 61 | |
| `4` | `Ꮞ` | 58 | |
| `1` | `Ꭲ` | 57 | |
| `;` | `Ꮆ` | 56 | |
| `Ꮎ` | `Ꮾ` | 51 | |
| `3` | `8` | 46 | |
| `Ꮎ` | `Ꭷ` | 45 | |
| `-` | `Ꮕ` | 44 | |
| `?` | `Ꭾ` | 40 | |
| `;` | `:` | 38 | |
| `.` | `,` | 37 | |
| `Ꮅ` | `Ꮲ` | 28 | |
| `Ꮢ` | `Ꭱ` | 25 | |
| `Ꮩ` | `Ꭺ` | 21 | |
| `Ꭸ` | `Ꭼ` | 21 | |
| `2` | `9` | 18 | |
| `Ꭸ` | `Ꮵ` | 18 | |
| `Ᏻ` | `Ꮸ` | 17 | |
| `]` | `)` | 17 | |
| `Ꮈ` | `Ꮔ` | 16 | |
| `Ꮥ` | `Ꭶ` | 14 | |
| `Ꮥ` | `Ꮕ` | 14 | |
| `Ꭸ` | `Ꮀ` | 14 | |
| `6` | `Ꮾ` | 13 | |
| `Ꭽ` | ` ` | 13 | |
| `Ᏻ` | `Ꮚ` | 13 | |

## Top 15 Deleted Characters
| Character | Deletion Count | Total in GT | Deletion Rate |
| :-------: | :------------: | :---------: | :------------: |
| `Ꭽ` | 84 | 271 | 31.00% |
| ` ` | 39 | 4632 | 0.84% |
| `-` | 22 | 527 | 4.17% |
| `Ꮝ` | 17 | 1568 | 1.08% |
| `Ꭴ` | 16 | 774 | 2.07% |
| `Ꮣ` | 10 | 602 | 1.66% |
| `Ꮧ` | 10 | 1096 | 0.91% |
| `Ꮕ` | 9 | 565 | 1.59% |
| `Ꮒ` | 8 | 765 | 1.05% |
| `Ꭲ` | 8 | 958 | 0.84% |
| `Ꭼ` | 8 | 411 | 1.95% |
| `Ꮎ` | 7 | 809 | 0.87% |
| `.` | 7 | 352 | 1.99% |
| `Ꮩ` | 6 | 369 | 1.63% |
| `,` | 6 | 572 | 1.05% |

## Top 15 Inserted Characters
| Character | Insertion Count |
| :-------: | :-------------: |
| ` ` | 132 |
| `.` | 111 |
| `-` | 65 |
| `Ꮨ` | 52 |
| `“` | 46 |
| `Ꮕ` | 46 |
| `Ꮵ` | 38 |
| `,` | 33 |
| `;` | 33 |
| `Ꭲ` | 31 |
| `Ꮭ` | 31 |
| `Ꮆ` | 30 |
| `:` | 29 |
| `Ꭷ` | 27 |
| `”` | 27 |

