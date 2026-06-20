# Parsing Debug Report

## Input
- file path: `C:\Users\ashuf\Desktop\haw\Sem_5\OS\10 OS-BS 2020 Interprocess communication E.pdf`
- file name: `10 OS-BS 2020 Interprocess communication E.pdf`
- file hash: `70326d55718a38e83c0d8c0546388cacaaa37061ce807c3bd96e13fd33a1e1e6`
- content hash: `70326d55718a38e83c0d8c0546388cacaaa37061ce807c3bd96e13fd33a1e1e6`
- report path: `C:\Users\ashuf\Desktop\Projects\document-ai-assistant\outputs\debug_parsing\10 OS-BS 2020 Interprocess communication E_parsing_report.md`

## Raw Parsed Document
- parser name: `docling`
- parser version: `2.102.2`
- title: `10 OS-BS 2020 Interprocess communication E`
- page count: `33`
- raw document type: `DoclingDocument`

## Canonical Elements Summary
- total canonical elements: `224`
- count by element_type: `{
  "code": 29,
  "list_item": 14,
  "picture": 52,
  "section_header": 42,
  "text": 87
}`
- page range: `1 -> 33`

### First 20 Elements
| order_index | element_id | element_type | page_start | page_end | section_title | text preview |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | #/texts/0 | section_header | 1 | 1 | Betriebssysteme / Operating Systems Interprocess Communication | Betriebssysteme / Operating Systems Interprocess Communication |
| 2 | #/texts/1 | text | 1 | 1 |  | SS 2020 |
| 3 | #/texts/2 | text | 1 | 1 |  | Prof. Dr.-Ing. Holger Gräßner |
| 4 | #/texts/3 | text | 1 | 1 |  | [10 OS-BS 2020 Interprocess communication.pptx] |
| 5 | #/pictures/0 | picture | 1 | 1 |  |  |
| 6 | #/texts/4 | text | 2 | 2 |  | DE |
| 7 | #/pictures/1 | picture | 2 | 2 |  |  |
| 8 | #/texts/5 | section_header | 2 | 2 | Signals | Signals |
| 9 | #/texts/6 | section_header | 2 | 2 | Signals | Signals |
| 10 | #/texts/7 | text | 2 | 2 |  | signal occurs |
| 11 | #/texts/8 | text | 2 | 2 |  | handler is called |
| 12 | #/texts/9 | text | 2 | 2 |  | return |
| 13 | #/texts/10 | text | 2 | 2 |  | Signal-Handler |
| 14 | #/pictures/2 | picture | 2 | 2 |  |  |
| 15 | #/texts/15 | section_header | 3 | 3 | Catching a signal with a signal handler (I) | Catching a signal with a signal handler (I) |
| 16 | #/texts/16 | code | 3 | 3 |  | #include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration *... |
| 17 | #/texts/17 | text | 3 | 3 |  | → signal_handler.c |
| 18 | #/pictures/3 | picture | 3 | 3 |  |  |
| 19 | #/texts/18 | text | 3 | 3 |  | DE |
| 20 | #/texts/23 | section_header | 4 | 4 | Catching a signal with a signal handler (II) | Catching a signal with a signal handler (II) |

## Canonical Elements Full Dump

### #/texts/0
- type: `section_header`
- order index: `1`
- page: `1`
- section title: `Betriebssysteme / Operating Systems Interprocess Communication`
- section path: ``
- bbox: `(28.632, 358.50224000000003) -> (531.0955200000001, 292.512442519337)`
- raw_ref: `#/texts/0`
- text/content preview: `Betriebssysteme / Operating Systems Interprocess Communication`

### #/texts/1
- type: `text`
- order index: `2`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(28.632, 248.75624000000005) -> (89.91641999999997, 234.33363491712709)`
- raw_ref: `#/texts/1`
- text/content preview: `SS 2020`

### #/texts/2
- type: `text`
- order index: `3`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(28.632, 197.12624) -> (235.06007999999997, 182.70363491712703)`
- raw_ref: `#/texts/2`
- text/content preview: `Prof. Dr.-Ing. Holger Gräßner`

### #/texts/3
- type: `text`
- order index: `4`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(28.632, 141.48576000000003) -> (208.64423999999997, 134.38208883977904)`
- raw_ref: `#/texts/3`
- text/content preview: `[10 OS-BS 2020 Interprocess communication.pptx]`

### #/pictures/0
- type: `picture`
- order index: `5`
- page: `1`
- section title: ``
- section path: ``
- bbox: `(486.7731628417969, 88.3543701171875) -> (683.4052124023438, 36.245635986328125)`
- raw_ref: `#/pictures/0`
- text/content preview: ``

### #/texts/4
- type: `text`
- order index: `6`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/4`
- text/content preview: `DE`

### #/pictures/1
- type: `picture`
- order index: `7`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(32.33742141723633, 532.1867089271545) -> (667.2354736328125, 64.11972045898438)`
- raw_ref: `#/pictures/1`
- text/content preview: ``

### #/texts/5
- type: `section_header`
- order index: `8`
- page: `2`
- section title: `Signals`
- section path: ``
- bbox: `(36.648, 529.18376) -> (85.91088, 516.6985197790054)`
- raw_ref: `#/texts/5`
- text/content preview: `Signals`

### #/texts/6
- type: `section_header`
- order index: `9`
- page: `2`
- section title: `Signals`
- section path: ``
- bbox: `(36.648, 481.64176) -> (101.56728000000001, 463.77495071823205)`
- raw_ref: `#/texts/6`
- text/content preview: `Signals`

### #/texts/7
- type: `text`
- order index: `10`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(112.87, 392.34) -> (206.284, 374.34)`
- raw_ref: `#/texts/7`
- text/content preview: `signal occurs`

### #/texts/8
- type: `text`
- order index: `11`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(537.62, 389.05) -> (656.0620000000001, 371.05)`
- raw_ref: `#/texts/8`
- text/content preview: `handler is called`

### #/texts/9
- type: `text`
- order index: `12`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(186.43, 82.88400000000001) -> (232.384, 64.88400000000001)`
- raw_ref: `#/texts/9`
- text/content preview: `return`

### #/texts/10
- type: `text`
- order index: `13`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(331.66666666666663, 110.0) -> (462.0, 88.66666666666669)`
- raw_ref: `#/texts/10`
- text/content preview: `Signal-Handler`

### #/pictures/2
- type: `picture`
- order index: `14`
- page: `2`
- section title: ``
- section path: ``
- bbox: `(560.805419921875, 49.137359619140625) -> (683.521240234375, 16.405029296875)`
- raw_ref: `#/pictures/2`
- text/content preview: ``

### #/texts/15
- type: `section_header`
- order index: `15`
- page: `3`
- section title: `Catching a signal with a signal handler (I)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (402.43423999999993, 463.77495071823205)`
- raw_ref: `#/texts/15`
- text/content preview: `Catching a signal with a signal handler (I)`

### #/texts/16
- type: `code`
- order index: `16`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(36.648, 431.791192) -> (599.6199999999999, 114.21124129651861)`
- raw_ref: `#/texts/16`
- text/content preview: `#include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration */ volatile sig atomic t flag = FALSE; int main() { signal(SIGINT,sigh); /* assign handler fuction */ printf ('Press ˆC to call the signal handler \ n');`

### #/texts/17
- type: `text`
- order index: `17`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(601.99, 76.694184) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/17`
- text/content preview: `→ signal_handler.c`

### #/pictures/3
- type: `picture`
- order index: `18`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(560.6714477539062, 48.936859130859375) -> (683.48779296875, 16.345703125)`
- raw_ref: `#/pictures/3`
- text/content preview: ``

### #/texts/18
- type: `text`
- order index: `19`
- page: `3`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/18`
- text/content preview: `DE`

### #/texts/23
- type: `section_header`
- order index: `20`
- page: `4`
- section title: `Catching a signal with a signal handler (II)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (407.9719999999999, 463.77495071823205)`
- raw_ref: `#/texts/23`
- text/content preview: `Catching a signal with a signal handler (II)`

### #/texts/24
- type: `code`
- order index: `21`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(36.648, 428.344) -> (524.4699999999999, 161.0374296182473)`
- raw_ref: `#/texts/24`
- text/content preview: `while (!flag) ; printf (' Program will be terminated!\ n'); return 0; } void sigh(int signum) { flag = TRUE; }`

### #/texts/25
- type: `text`
- order index: `22`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/25`
- text/content preview: `DE`

### #/texts/26
- type: `text`
- order index: `23`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(601.99, 76.694184) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/26`
- text/content preview: `→ signal_handler.c`

### #/pictures/4
- type: `picture`
- order index: `24`
- page: `4`
- section title: ``
- section path: ``
- bbox: `(560.7781372070312, 48.928131103515625) -> (683.4304809570312, 16.3720703125)`
- raw_ref: `#/pictures/4`
- text/content preview: ``

### #/texts/31
- type: `section_header`
- order index: `25`
- page: `5`
- section title: `Process synchronisation with a signal (I)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (393.56408, 463.77495071823205)`
- raw_ref: `#/texts/31`
- text/content preview: `Process synchronisation with a signal (I)`

### #/texts/32
- type: `code`
- order index: `26`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(36.648, 431.791192) -> (477.67, 95.4894296182473)`
- raw_ref: `#/texts/32`
- text/content preview: `#include <stdio.h> #include <signal.h> #include <unistd.h> #include <sys/wait.h> #include <sys/types.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration */ int main(void) { pid t npid; int status; npid = fork();`

### #/texts/33
- type: `text`
- order index: `27`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/33`
- text/content preview: `DE`

### #/texts/34
- type: `text`
- order index: `28`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(589.99, 76.694184) -> (710.9404000000001, 67.29928344777909)`
- raw_ref: `#/texts/34`
- text/content preview: `→ proc_sync_signal.c`

### #/pictures/5
- type: `picture`
- order index: `29`
- page: `5`
- section title: ``
- section path: ``
- bbox: `(560.6431884765625, 48.949737548828125) -> (683.483642578125, 16.42071533203125)`
- raw_ref: `#/pictures/5`
- text/content preview: ``

### #/texts/39
- type: `section_header`
- order index: `30`
- page: `6`
- section title: `Process synchronisation with a signal (II)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (399.10184, 463.77495071823205)`
- raw_ref: `#/texts/39`
- text/content preview: `Process synchronisation with a signal (II)`

### #/texts/40
- type: `code`
- order index: `31`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(72.648, 428.344) -> (689.42, 133.1712412965186)`
- raw_ref: `#/texts/40`
- text/content preview: `if (npid) { printf ('Parent process: Press CR to send SIGUSR1 to child process!\ n'); getchar() ; kill (npid, SIGUSR1); /* send SIGUSR1 to child npid */ printf ('Parent process: SIGUSR1 has been send.\ n'); wait(&status); printf ('Parent process: Child process terminated, exit state = %i\ n', WEXITSTATUS( status));...`

### #/pictures/6
- type: `picture`
- order index: `32`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(588.8361206054688, 77.61093139648438) -> (710.9244995117188, 65.33694458007812)`
- raw_ref: `#/pictures/6`
- text/content preview: ``

### #/texts/41
- type: `text`
- order index: `33`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(589.99, 76.694184) -> (710.9404000000001, 67.29928344777909)`
- raw_ref: `#/texts/41`
- text/content preview: `→ proc_sync_signal.c`

### #/pictures/7
- type: `picture`
- order index: `34`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(560.6157836914062, 48.907379150390625) -> (683.4541625976562, 16.37677001953125)`
- raw_ref: `#/pictures/7`
- text/content preview: ``

### #/texts/42
- type: `text`
- order index: `35`
- page: `6`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/42`
- text/content preview: `DE`

### #/texts/47
- type: `section_header`
- order index: `36`
- page: `7`
- section title: `Process synchronisation with a signal (III)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (404.6396, 463.77495071823205)`
- raw_ref: `#/texts/47`
- text/content preview: `Process synchronisation with a signal (III)`

### #/texts/48
- type: `code`
- order index: `37`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(36.648, 428.344) -> (711.0199999999999, 67.29928344777909)`
- raw_ref: `#/texts/48`
- text/content preview: `else { printf ('Child process: Waiting for signal...\ n'); signal(SIGUSR1, sigh); /* assign SIGUSR1 to handler */ pause(); /* block until signal */ printf ('Child process: SIGUSR1 received! End in 1s\ n'); sleep(1); return 55; } } void sigh(int signum) /* Signal handler for SIGUSR1 */ { /* attention: only reentrant...`

### #/pictures/8
- type: `picture`
- order index: `38`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(560.4451904296875, 49.04803466796875) -> (683.5855102539062, 16.3685302734375)`
- raw_ref: `#/pictures/8`
- text/content preview: ``

### #/texts/49
- type: `text`
- order index: `39`
- page: `7`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/49`
- text/content preview: `DE`

### #/texts/53
- type: `section_header`
- order index: `40`
- page: `8`
- section title: `Signals`
- section path: ``
- bbox: `(36.648, 529.18376) -> (85.91088, 516.6985197790054)`
- raw_ref: `#/texts/53`
- text/content preview: `Signals`

### #/texts/54
- type: `section_header`
- order index: `41`
- page: `8`
- section title: `Basic signal handling`
- section path: ``
- bbox: `(36.648, 481.64176) -> (223.92904000000004, 463.77495071823205)`
- raw_ref: `#/texts/54`
- text/content preview: `Basic signal handling`

### #/texts/55
- type: `code`
- order index: `42`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(36.648, 426.40864) -> (556.6948000000002, 413.6761755582233)`
- raw_ref: `#/texts/55`
- text/content preview: `sighandler_t signal (int signum, sighandler_t action);`

### #/texts/56
- type: `section_header`
- order index: `43`
- page: `8`
- section title: `Parameter:`
- section path: ``
- bbox: `(36.648, 377.75624) -> (116.17968, 363.3336349171271)`
- raw_ref: `#/texts/56`
- text/content preview: `Parameter:`

### #/texts/57
- type: `text`
- order index: `44`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(36.648, 327.853712) -> (322.01691200000005, 313.409580640884)`
- raw_ref: `#/texts/57`
- text/content preview: `signum : Signal to specify it's behaviour.`

### #/texts/58
- type: `text`
- order index: `45`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(36.648, 302.84623999999997) -> (187.44768, 288.42363491712706)`
- raw_ref: `#/texts/58`
- text/content preview: `action : New action:`

### #/texts/59
- type: `list_item`
- order index: `46`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(36.648, 277.903712) -> (331.616912, 263.459580640884)`
- raw_ref: `#/texts/59`
- text/content preview: `-SIG_DFL : Default action for this signal.`

### #/texts/60
- type: `list_item`
- order index: `47`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(36.648, 252.90624000000003) -> (541.45028, 238.48363491712706)`
- raw_ref: `#/texts/60`
- text/content preview: `-SIG_IGN : Ignore this signal (not possible for SIGKILL or SIGSTOP ).`

### #/texts/61
- type: `list_item`
- order index: `48`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(36.648, 227.963712) -> (303.996912, 213.519580640884)`
- raw_ref: `#/texts/61`
- text/content preview: `-Adress of a signal handler function.`

### #/pictures/9
- type: `picture`
- order index: `49`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(560.7848510742188, 48.889617919921875) -> (683.1738891601562, 16.360107421875)`
- raw_ref: `#/pictures/9`
- text/content preview: ``

### #/texts/62
- type: `text`
- order index: `50`
- page: `8`
- section title: ``
- section path: ``
- bbox: `(689.06, 526.4) -> (710.4929599999999, 482.47999999999996)`
- raw_ref: `#/texts/62`
- text/content preview: `E`

### #/texts/66
- type: `section_header`
- order index: `51`
- page: `9`
- section title: `Signals`
- section path: ``
- bbox: `(36.648, 529.18376) -> (85.91088, 516.6985197790054)`
- raw_ref: `#/texts/66`
- text/content preview: `Signals`

### #/texts/67
- type: `section_header`
- order index: `52`
- page: `9`
- section title: `Advanced signal handling (I)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (289.10423999999995, 463.77495071823205)`
- raw_ref: `#/texts/67`
- text/content preview: `Advanced signal handling (I)`

### #/texts/68
- type: `section_header`
- order index: `53`
- page: `9`
- section title: `Function sigaction :`
- section path: ``
- bbox: `(36.648, 427.69624) -> (200.45463999999998, 413.2736349171271)`
- raw_ref: `#/texts/68`
- text/content preview: `Function sigaction :`

### #/texts/69
- type: `text`
- order index: `54`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(36.648, 401.44863999999995) -> (691.7111200000004, 367.59236387995196)`
- raw_ref: `#/texts/69`
- text/content preview: `int sigaction (int signum, const struct sigaction *restrict action, struct sigaction *restrict old-action);`

### #/texts/70
- type: `section_header`
- order index: `55`
- page: `9`
- section title: `Parameter:`
- section path: ``
- bbox: `(36.648, 356.63624) -> (116.17968, 342.2136349171271)`
- raw_ref: `#/texts/70`
- text/content preview: `Parameter:`

### #/texts/71
- type: `list_item`
- order index: `56`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(36.648, 306.68624) -> (130.42028, 292.2636349171271)`
- raw_ref: `#/texts/71`
- text/content preview: `signum :`

### #/texts/72
- type: `text`
- order index: `57`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(180.7, 306.68624) -> (399.32024, 292.2636349171271)`
- raw_ref: `#/texts/72`
- text/content preview: `Signal to specify it's behaviour.`

### #/texts/73
- type: `list_item`
- order index: `58`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(36.648, 281.74371199999996) -> (307.2623999999999, 267.29958064088396)`
- raw_ref: `#/texts/73`
- text/content preview: `action : New action. NULL`

### #/texts/74
- type: `text`
- order index: `59`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(307.2, 281.74371199999996) -> (489.58691200000004, 267.29958064088396)`
- raw_ref: `#/texts/74`
- text/content preview: `: No change of behaviour.`

### #/texts/75
- type: `list_item`
- order index: `60`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(36.648, 256.74624) -> (498.46028, 242.32363491712704)`
- raw_ref: `#/texts/75`
- text/content preview: `old-action : Get information about the current behaviour.`

### #/texts/76
- type: `text`
- order index: `61`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(180.7, 234.09864) -> (219.14799999999997, 221.3661755582233)`
- raw_ref: `#/texts/76`
- text/content preview: `NULL`

### #/texts/77
- type: `text`
- order index: `62`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(219.1, 235.62624) -> (399.80024, 221.20363491712703)`
- raw_ref: `#/texts/77`
- text/content preview: `: No information required.`

### #/pictures/10
- type: `picture`
- order index: `63`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(560.7531127929688, 48.820037841796875) -> (683.1976318359375, 16.430908203125)`
- raw_ref: `#/pictures/10`
- text/content preview: ``

### #/texts/78
- type: `text`
- order index: `64`
- page: `9`
- section title: ``
- section path: ``
- bbox: `(689.06, 526.4) -> (710.4929599999999, 482.47999999999996)`
- raw_ref: `#/texts/78`
- text/content preview: `E`

### #/texts/83
- type: `section_header`
- order index: `65`
- page: `10`
- section title: `Advanced signal handling(II)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (288.40199999999993, 463.77495071823205)`
- raw_ref: `#/texts/83`
- text/content preview: `Advanced signal handling(II)`

### #/texts/84
- type: `text`
- order index: `66`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 453.51376) -> (308.90976, 441.02851977900553)`
- raw_ref: `#/texts/84`
- text/content preview: `Structure sigaction with some elements:`

### #/texts/85
- type: `code`
- order index: `67`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 413.28136) -> (237.98200000000006, 402.2592266026411)`
- raw_ref: `#/texts/85`
- text/content preview: `sighandler_t sa_handler`

### #/texts/86
- type: `section_header`
- order index: `68`
- page: `10`
- section title: `New action:`
- section path: ``
- bbox: `(36.648, 392.76376) -> (109.41976, 380.27851977900553)`
- raw_ref: `#/texts/86`
- text/content preview: `New action:`

### #/texts/87
- type: `list_item`
- order index: `69`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 370.90376) -> (295.22976, 358.4185197790055)`
- raw_ref: `#/texts/87`
- text/content preview: `-SIG_DFL : Default action for this signal.`

### #/texts/88
- type: `list_item`
- order index: `70`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 349.06376) -> (478.17972, 336.57851977900555)`
- raw_ref: `#/texts/88`
- text/content preview: `-SIG_IGN : Ignore this signal (not possible for SIGKILL or SIGSTOP ).`

### #/texts/89
- type: `list_item`
- order index: `71`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 327.24123199999997) -> (337.016432, 314.7344655027624)`
- raw_ref: `#/texts/89`
- text/content preview: `-Handler : Adress of a signal handler function.`

### #/texts/90
- type: `code`
- order index: `72`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 288.07376) -> (186.96972000000002, 275.58851977900554)`
- raw_ref: `#/texts/90`
- text/content preview: `sigset_t sa_mask :`

### #/texts/91
- type: `text`
- order index: `73`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 269.611232) -> (427.52646400000003, 257.1044655027624)`
- raw_ref: `#/texts/91`
- text/content preview: `Specifies a set of signals to block, while the handler is running.`

### #/texts/92
- type: `text`
- order index: `74`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 251.09375999999997) -> (548.28976, 220.1285197790055)`
- raw_ref: `#/texts/92`
- text/content preview: `Should be defined by usage of the functions sigemptyset() and sigaddset() , or sigfillset() and sigdelset() .`

### #/texts/93
- type: `code`
- order index: `75`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 193.71375999999998) -> (153.33972000000003, 181.22851977900552)`
- raw_ref: `#/texts/93`
- text/content preview: `int sa_flags :`

### #/texts/94
- type: `text`
- order index: `76`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 175.23375999999996) -> (270.50975999999997, 162.7485197790055)`
- raw_ref: `#/texts/94`
- text/content preview: `Flags to define the signal's behaviour:`

### #/texts/95
- type: `list_item`
- order index: `77`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 153.36375999999996) -> (486.74199999999996, 140.8785197790055)`
- raw_ref: `#/texts/95`
- text/content preview: `-e. g. SA_RESTART : Library functions like open() , read() , write()`

### #/texts/96
- type: `text`
- order index: `78`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(180.7, 134.88376) -> (505.29976, 122.39851977900554)`
- raw_ref: `#/texts/96`
- text/content preview: `will be resumed after execution of the signal handler.`

### #/texts/97
- type: `text`
- order index: `79`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(36.648, 113.06123200000002) -> (589.8097600000001, 82.0565197790055)`
- raw_ref: `#/texts/97`
- text/content preview: `-NULL : Library functions like open() , read() , write() ) will be terminated with errors after execution of the signal handler.`

### #/pictures/11
- type: `picture`
- order index: `80`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(560.699462890625, 48.846343994140625) -> (683.1425170898438, 16.43304443359375)`
- raw_ref: `#/pictures/11`
- text/content preview: ``

### #/texts/98
- type: `text`
- order index: `81`
- page: `10`
- section title: ``
- section path: ``
- bbox: `(689.06, 526.4) -> (710.4929599999999, 482.47999999999996)`
- raw_ref: `#/texts/98`
- text/content preview: `E`

### #/texts/102
- type: `section_header`
- order index: `82`
- page: `11`
- section title: `Signals`
- section path: ``
- bbox: `(36.648, 529.18376) -> (85.91088, 516.6985197790054)`
- raw_ref: `#/texts/102`
- text/content preview: `Signals`

### #/texts/103
- type: `section_header`
- order index: `83`
- page: `11`
- section title: `Usage of signal sets (I)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (241.08424000000002, 463.77495071823205)`
- raw_ref: `#/texts/103`
- text/content preview: `Usage of signal sets (I)`

### #/texts/104
- type: `code`
- order index: `84`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(36.648, 425.50600000000003) -> (316.3120000000001, 108.21124129651861)`
- raw_ref: `#/texts/104`
- text/content preview: `#include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) sig_atomic_t flag = FALSE; void sigh(int); int main() { sigset_t set; struct sigaction act;`

### #/texts/105
- type: `text`
- order index: `85`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/105`
- text/content preview: `DE`

### #/pictures/12
- type: `picture`
- order index: `86`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(625.2288208007812, 77.70004272460938) -> (710.9901123046875, 64.43295288085938)`
- raw_ref: `#/pictures/12`
- text/content preview: ``

### #/texts/106
- type: `text`
- order index: `87`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(626.02, 76.694184) -> (635.9118159999999, 70.68040458286987)`
- raw_ref: `#/texts/106`
- text/content preview: `→`

### #/texts/107
- type: `text`
- order index: `88`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(638.5, 75.29983199999998) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/107`
- text/content preview: `signal_set.c`

### #/pictures/13
- type: `picture`
- order index: `89`
- page: `11`
- section title: ``
- section path: ``
- bbox: `(560.740478515625, 48.841583251953125) -> (683.4296875, 16.3922119140625)`
- raw_ref: `#/pictures/13`
- text/content preview: ``

### #/texts/112
- type: `section_header`
- order index: `90`
- page: `12`
- section title: `Usage of signal sets (II)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (246.622, 463.77495071823205)`
- raw_ref: `#/texts/112`
- text/content preview: `Usage of signal sets (II)`

### #/texts/113
- type: `code`
- order index: `91`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(36.648, 422.104) -> (610.4199999999998, 98.8474296182473)`
- raw_ref: `#/texts/113`
- text/content preview: `sigemptyset(&set); sigaddset(&set, SIGINT); act.sa_flags = 0; act.sa_mask = set; act.sa_handler = &sigh; sigaction(SIGINT, &act, NULL); printf ('Press ˆC to call the signal handler!\ n'); while (!flag) ; printf ('Programm terminates now!\ n'); return 0; }`

### #/pictures/14
- type: `picture`
- order index: `92`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(625.1753540039062, 77.68136596679688) -> (710.925048828125, 64.50106811523438)`
- raw_ref: `#/pictures/14`
- text/content preview: ``

### #/texts/114
- type: `text`
- order index: `93`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(626.02, 76.694184) -> (635.9118159999999, 70.68040458286987)`
- raw_ref: `#/texts/114`
- text/content preview: `→`

### #/texts/115
- type: `text`
- order index: `94`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(638.5, 75.29983199999998) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/115`
- text/content preview: `signal_set.c`

### #/pictures/15
- type: `picture`
- order index: `95`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(560.6299438476562, 48.868621826171875) -> (683.3995971679688, 16.3658447265625)`
- raw_ref: `#/pictures/15`
- text/content preview: ``

### #/texts/116
- type: `text`
- order index: `96`
- page: `12`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/116`
- text/content preview: `DE`

### #/texts/120
- type: `section_header`
- order index: `97`
- page: `13`
- section title: `Signals`
- section path: ``
- bbox: `(36.648, 529.18376) -> (85.91088, 516.6985197790054)`
- raw_ref: `#/texts/120`
- text/content preview: `Signals`

### #/texts/121
- type: `section_header`
- order index: `98`
- page: `13`
- section title: `Usage of signal sets (III)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (252.15976, 463.77495071823205)`
- raw_ref: `#/texts/121`
- text/content preview: `Usage of signal sets (III)`

### #/texts/122
- type: `code`
- order index: `99`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(36.648, 422.104) -> (262.8, 323.5874296182473)`
- raw_ref: `#/texts/122`
- text/content preview: `void sigh(int signum) { flag = TRUE; }`

### #/texts/123
- type: `text`
- order index: `100`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/123`
- text/content preview: `DE`

### #/pictures/16
- type: `picture`
- order index: `101`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(625.3656616210938, 77.67584228515625) -> (710.96337890625, 64.2947998046875)`
- raw_ref: `#/pictures/16`
- text/content preview: ``

### #/texts/124
- type: `text`
- order index: `102`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(626.02, 76.694184) -> (635.9118159999999, 70.68040458286987)`
- raw_ref: `#/texts/124`
- text/content preview: `→`

### #/texts/125
- type: `text`
- order index: `103`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(638.5, 75.29983199999998) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/125`
- text/content preview: `signal_set.c`

### #/pictures/17
- type: `picture`
- order index: `104`
- page: `13`
- section title: ``
- section path: ``
- bbox: `(560.8382568359375, 48.85980224609375) -> (683.3323974609375, 16.3985595703125)`
- raw_ref: `#/pictures/17`
- text/content preview: ``

### #/texts/129
- type: `section_header`
- order index: `105`
- page: `14`
- section title: `Signals`
- section path: ``
- bbox: `(36.648, 529.18376) -> (85.91088, 516.6985197790054)`
- raw_ref: `#/texts/129`
- text/content preview: `Signals`

### #/texts/130
- type: `text`
- order index: `106`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/130`
- text/content preview: `DE`

### #/pictures/18
- type: `picture`
- order index: `107`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(34.33107376098633, 521.909122467041) -> (685.432861328125, 62.417236328125)`
- raw_ref: `#/pictures/18`
- text/content preview: ``

### #/texts/131
- type: `text`
- order index: `108`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(36.648, 481.64176) -> (156.591304, 437.370896441989)`
- raw_ref: `#/texts/131`
- text/content preview: `sigsetjmp() siglongjump()`

### #/texts/132
- type: `text`
- order index: `109`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(191.42, 497.44) -> (291.97999999999996, 436.21)`
- raw_ref: `#/texts/132`
- text/content preview: `Define poit of reentry with sigsetjmp()`

### #/texts/133
- type: `text`
- order index: `110`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(213.79, 286.84) -> (307.20399999999984, 268.84)`
- raw_ref: `#/texts/133`
- text/content preview: `signal occurs`

### #/texts/134
- type: `text`
- order index: `111`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(627.1, 292.91) -> (685.0507120000001, 253.30399999999997)`
- raw_ref: `#/texts/134`
- text/content preview: `Handler is called`

### #/texts/135
- type: `text`
- order index: `112`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(167.02, 136.19) -> (285.83, 74.964)`
- raw_ref: `#/texts/135`
- text/content preview: `jump to point of reentry with siglongjmp()`

### #/texts/136
- type: `text`
- order index: `113`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(392.0, 102.0) -> (523.6666666666667, 81.66666666666669)`
- raw_ref: `#/texts/136`
- text/content preview: `Signal-Handler`

### #/pictures/19
- type: `picture`
- order index: `114`
- page: `14`
- section title: ``
- section path: ``
- bbox: `(560.9716186523438, 49.09503173828125) -> (683.40283203125, 16.4447021484375)`
- raw_ref: `#/pictures/19`
- text/content preview: ``

### #/texts/141
- type: `section_header`
- order index: `115`
- page: `15`
- section title: `sigsetjmp() and siglongjump()`
- section path: ``
- bbox: `(36.648, 481.64176) -> (298.71331999999995, 463.77495071823205)`
- raw_ref: `#/texts/141`
- text/content preview: `sigsetjmp() and siglongjump()`

### #/texts/142
- type: `text`
- order index: `116`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(36.648, 428.344) -> (480.54400000000004, 104.66523854143645)`
- raw_ref: `#/texts/142`
- text/content preview: `sigsetjmp(env,smask); env: adress of environment buffer smask: ≠ 0: include signal mask Return value : = 0 : first call (definition of jump label) ≠ 0 : following calls (jump to label) siglongjmp(env,ret); env: adress of environment buffer ret: ≠ 0: second call of sigsetjmp()`

### #/texts/143
- type: `text`
- order index: `117`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/143`
- text/content preview: `DE`

### #/pictures/20
- type: `picture`
- order index: `118`
- page: `15`
- section title: ``
- section path: ``
- bbox: `(560.844970703125, 48.84344482421875) -> (683.1758422851562, 16.4356689453125)`
- raw_ref: `#/pictures/20`
- text/content preview: ``

### #/texts/148
- type: `section_header`
- order index: `119`
- page: `16`
- section title: `Usage of sigsetjmp() and siglongjump() (I)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (408.8074399999999, 463.77495071823205)`
- raw_ref: `#/texts/148`
- text/content preview: `Usage of sigsetjmp() and siglongjump() (I)`

### #/texts/149
- type: `code`
- order index: `120`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(36.648, 431.791192) -> (471.68440000000004, 86.34924129651858)`
- raw_ref: `#/texts/149`
- text/content preview: `#include <stdio.h> #include <signal.h> #include <setjmp.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); Sigjmp_buf env; int main() { int retval; signal(SIGINT,sigh);`

### #/texts/150
- type: `text`
- order index: `121`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/150`
- text/content preview: `DE`

### #/pictures/21
- type: `picture`
- order index: `122`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(625.2733154296875, 77.71163940429688) -> (710.8555908203125, 65.19207763671875)`
- raw_ref: `#/pictures/21`
- text/content preview: ``

### #/texts/151
- type: `text`
- order index: `123`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(626.02, 76.694184) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/151`
- text/content preview: `→ siglongjmp.c`

### #/pictures/22
- type: `picture`
- order index: `124`
- page: `16`
- section title: ``
- section path: ``
- bbox: `(560.7233276367188, 48.85955810546875) -> (683.3724975585938, 16.36785888671875)`
- raw_ref: `#/pictures/22`
- text/content preview: ``

### #/texts/156
- type: `section_header`
- order index: `125`
- page: `17`
- section title: `Usage of sigsetjmp() and siglongjump() (II)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (414.34519999999986, 463.77495071823205)`
- raw_ref: `#/texts/156`
- text/content preview: `Usage of sigsetjmp() and siglongjump() (II)`

### #/texts/157
- type: `code`
- order index: `126`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(36.648, 450.229192) -> (677.414, 70.68040458286987)`
- raw_ref: `#/texts/157`
- text/content preview: `if (( ret val = sigsetjmp(env,0)) == 0) {// first call printf (' sigsetjmp() has been initialised. Return value was %d.\n -> endless loop\ n', retval); while (1) ; } else // following calls printf ('Return value of sigsetjmp() was now %d.\n -> EXIT!\n ', retval); return 0; } void sigh(int signum) { siglongjmp(env,TR...`

### #/texts/158
- type: `text`
- order index: `127`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/158`
- text/content preview: `DE`

### #/texts/159
- type: `text`
- order index: `128`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(638.5, 75.29983199999998) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/159`
- text/content preview: `siglongjmp.c`

### #/pictures/23
- type: `picture`
- order index: `129`
- page: `17`
- section title: ``
- section path: ``
- bbox: `(560.612548828125, 48.942169189453125) -> (683.4868774414062, 16.27960205078125)`
- raw_ref: `#/pictures/23`
- text/content preview: ``

### #/texts/163
- type: `section_header`
- order index: `130`
- page: `18`
- section title: `Pipes and FIFOs`
- section path: ``
- bbox: `(36.648, 529.18376) -> (145.70872, 516.6985197790054)`
- raw_ref: `#/texts/163`
- text/content preview: `Pipes and FIFOs`

### #/texts/164
- type: `section_header`
- order index: `131`
- page: `18`
- section title: `Usage of pipes and FIFOs`
- section path: ``
- bbox: `(36.648, 481.64176) -> (270.05704, 463.77495071823205)`
- raw_ref: `#/texts/164`
- text/content preview: `Usage of pipes and FIFOs`

### #/texts/165
- type: `code`
- order index: `132`
- page: `18`
- section title: ``
- section path: ``
- bbox: `(36.648, 428.344) -> (522.3480159999999, 132.93124129651858)`
- raw_ref: `#/texts/165`
- text/content preview: `int fds[2], rval; rval = pipe(fds); // create pipe write(fds [1], ...); // write access read(fds [0], ...) ; // read access int fds, rval ; rval = mkfifo(name,rights); // create FIFO fds = open(name,mode) // open FIFO write(fds, ...); // write access read(fds, ...); // read access`

### #/texts/166
- type: `text`
- order index: `133`
- page: `18`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/166`
- text/content preview: `DE`

### #/pictures/24
- type: `picture`
- order index: `134`
- page: `18`
- section title: ``
- section path: ``
- bbox: `(560.6564331054688, 48.912750244140625) -> (683.2906494140625, 16.4149169921875)`
- raw_ref: `#/pictures/24`
- text/content preview: ``

### #/texts/171
- type: `section_header`
- order index: `135`
- page: `19`
- section title: `Message transmission with pipe() (I)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (357.68743999999987, 463.77495071823205)`
- raw_ref: `#/texts/171`
- text/content preview: `Message transmission with pipe() (I)`

### #/texts/172
- type: `code`
- order index: `136`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(36.648, 431.791192) -> (493.2844, 67.3892412965186)`
- raw_ref: `#/texts/172`
- text/content preview: `#include <stdio.h> #include <stdlib.h> #include <sys/types.h> #include <sys/stat.h> #include <errno.h> int main(void) { pid_t npid; size_t anz; int fds[2]; char msgbuf [100]=' \ 0'; if (pipe(fds) < 0) { perror ('Pipe'); return EXIT FAILURE; }`

### #/texts/173
- type: `text`
- order index: `137`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/173`
- text/content preview: `DE`

### #/pictures/25
- type: `picture`
- order index: `138`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(661.056884765625, 77.65426635742188) -> (710.8728637695312, 65.43826293945312)`
- raw_ref: `#/pictures/25`
- text/content preview: ``

### #/texts/174
- type: `text`
- order index: `139`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(662.02, 76.694184) -> (710.5824, 67.29928344777909)`
- raw_ref: `#/texts/174`
- text/content preview: `→ pipe.c`

### #/pictures/26
- type: `picture`
- order index: `140`
- page: `19`
- section title: ``
- section path: ``
- bbox: `(560.5835571289062, 48.89166259765625) -> (683.3668823242188, 16.40643310546875)`
- raw_ref: `#/pictures/26`
- text/content preview: ``

### #/texts/179
- type: `section_header`
- order index: `141`
- page: `20`
- section title: `Message transmission with pipe() (II)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (363.22519999999986, 463.77495071823205)`
- raw_ref: `#/texts/179`
- text/content preview: `Message transmission with pipe() (II)`

### #/texts/180
- type: `code`
- order index: `142`
- page: `20`
- section title: ``
- section path: ``
- bbox: `(72.648, 428.344) -> (517.5160000000001, 161.2774296182473)`
- raw_ref: `#/texts/180`
- text/content preview: `npid = fork(); if (npid) { printf ('Parent process: please type a message:\ n'); fflush (stdin); scanf ('%[ˆ \ n]', msgbuf); anz = strlen (msgbuf)+1; write(fds[1], msgbuf, anz); printf ('Parent process: EXIT\ n'); }`

### #/texts/181
- type: `text`
- order index: `143`
- page: `20`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/181`
- text/content preview: `DE`

### #/pictures/27
- type: `picture`
- order index: `144`
- page: `20`
- section title: ``
- section path: ``
- bbox: `(661.283935546875, 77.59860229492188) -> (710.9486083984375, 65.44003295898438)`
- raw_ref: `#/pictures/27`
- text/content preview: ``

### #/texts/182
- type: `text`
- order index: `145`
- page: `20`
- section title: ``
- section path: ``
- bbox: `(662.02, 76.694184) -> (671.9118159999999, 70.68040458286987)`
- raw_ref: `#/texts/182`
- text/content preview: `→`

### #/texts/183
- type: `text`
- order index: `146`
- page: `20`
- section title: ``
- section path: ``
- bbox: `(674.52, 75.29983199999998) -> (710.5824, 67.29928344777909)`
- raw_ref: `#/texts/183`
- text/content preview: `pipe.c`

### #/pictures/28
- type: `picture`
- order index: `147`
- page: `20`
- section title: ``
- section path: ``
- bbox: `(560.729248046875, 48.869720458984375) -> (683.471435546875, 16.40240478515625)`
- raw_ref: `#/pictures/28`
- text/content preview: ``

### #/texts/188
- type: `section_header`
- order index: `148`
- page: `21`
- section title: `Message transmission with pipe() (III)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (368.76295999999985, 463.77495071823205)`
- raw_ref: `#/texts/188`
- text/content preview: `Message transmission with pipe() (III)`

### #/texts/189
- type: `text`
- order index: `149`
- page: `21`
- section title: ``
- section path: ``
- bbox: `(36.648, 147.18399999999997) -> (47.448, 132.93124129651858)`
- raw_ref: `#/texts/189`
- text/content preview: `}`

### #/texts/190
- type: `code`
- order index: `150`
- page: `21`
- section title: ``
- section path: ``
- bbox: `(72.648, 428.344) -> (700.2719999999998, 105.91929281767955)`
- raw_ref: `#/texts/190`
- text/content preview: `else { printf ('Child process: waiting for message...\ n'); if ((anz=read(fds[0], msgbuf, sizeof(msgbuf))) != -1) { printf ('Child process: I received this message: \n %s\ n', msgbuf); printf ('Child process: EXIT\ n'); } else printf ('Child process: No message for me! (error %s)!\ n', strerror(errno)); } Properties...`

### #/texts/191
- type: `list_item`
- order index: `151`
- page: `21`
- section title: ``
- section path: ``
- bbox: `(117.43, 100.481472) -> (256.80757600000004, 84.31523854143643)`
- raw_ref: `#/texts/191`
- text/content preview: `easy and fast.`

### #/texts/192
- type: `section_header`
- order index: `152`
- page: `21`
- section title: `→ Skat exercise using pipes!`
- section path: ``
- bbox: `(308.04, 79.78199999999998) -> (556.984, 62.863292817679564)`
- raw_ref: `#/texts/192`
- text/content preview: `→ Skat exercise using pipes!`

### #/texts/193
- type: `text`
- order index: `153`
- page: `21`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/193`
- text/content preview: `DE`

### #/pictures/29
- type: `picture`
- order index: `154`
- page: `21`
- section title: ``
- section path: ``
- bbox: `(661.0276489257812, 77.69424438476562) -> (710.9013671875, 65.3553466796875)`
- raw_ref: `#/pictures/29`
- text/content preview: ``

### #/texts/194
- type: `text`
- order index: `155`
- page: `21`
- section title: ``
- section path: ``
- bbox: `(662.02, 76.694184) -> (671.9118159999999, 70.68040458286987)`
- raw_ref: `#/texts/194`
- text/content preview: `→`

### #/texts/195
- type: `text`
- order index: `156`
- page: `21`
- section title: ``
- section path: ``
- bbox: `(674.52, 75.29983199999998) -> (710.5824, 67.29928344777909)`
- raw_ref: `#/texts/195`
- text/content preview: `pipe.c`

### #/pictures/30
- type: `picture`
- order index: `157`
- page: `21`
- section title: ``
- section path: ``
- bbox: `(560.6783447265625, 48.89697265625) -> (683.409912109375, 16.3321533203125)`
- raw_ref: `#/pictures/30`
- text/content preview: ``

### #/texts/200
- type: `section_header`
- order index: `158`
- page: `22`
- section title: `Message transmission with FIFO (I)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (351.9400799999999, 463.77495071823205)`
- raw_ref: `#/texts/200`
- text/content preview: `Message transmission with FIFO (I)`

### #/texts/201
- type: `code`
- order index: `159`
- page: `22`
- section title: ``
- section path: ``
- bbox: `(36.648, 431.791192) -> (660.3743999999999, 86.10924129651858)`
- raw_ref: `#/texts/201`
- text/content preview: `#include <stdio.h> #include <stdlib.h> #include <sys/types.h> #include <sys/stat.h> #include <fcntl.h> #include <errno.h> // Note: FIFOs will not run on a Windows NTFS file system! #define TFIFO ' tfifo ' #define BUFLEN 100 #define MODE (S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH | S_IWOTH) int main(void) { pid...`

### #/pictures/31
- type: `picture`
- order index: `160`
- page: `22`
- section title: ``
- section path: ``
- bbox: `(661.271484375, 77.329833984375) -> (710.8663330078125, 67.65499877929688)`
- raw_ref: `#/pictures/31`
- text/content preview: ``

### #/pictures/32
- type: `picture`
- order index: `161`
- page: `22`
- section title: ``
- section path: ``
- bbox: `(560.60986328125, 48.871917724609375) -> (683.364501953125, 16.3936767578125)`
- raw_ref: `#/pictures/32`
- text/content preview: ``

### #/texts/203
- type: `text`
- order index: `162`
- page: `22`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/203`
- text/content preview: `DE`

### #/texts/208
- type: `section_header`
- order index: `163`
- page: `23`
- section title: `Message transmission with FIFO (II)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (357.4778399999999, 463.77495071823205)`
- raw_ref: `#/texts/208`
- text/content preview: `Message transmission with FIFO (II)`

### #/texts/209
- type: `code`
- order index: `164`
- page: `23`
- section title: ``
- section path: ``
- bbox: `(72.648, 450.229192) -> (711.0199999999999, 70.50924129651861)`
- raw_ref: `#/texts/209`
- text/content preview: `if (mkfifo(fifo_nam, MODE) < 0) { printf ('Error creating FIFO (%s)!\ n', strerror(errno)); return EXIT FAILURE; } npid = fork(); if (npid) { if ((fds=open(fifo_nam, O_WRONLY)) == -1) { printf ('Parent process: Could't open FIFO for writing (%s)!\ n', strerror(errno)); return EXIT FAILURE; } printf ('Parent process:...`

### #/texts/210
- type: `text`
- order index: `165`
- page: `23`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/210`
- text/content preview: `DE`

### #/pictures/33
- type: `picture`
- order index: `166`
- page: `23`
- section title: ``
- section path: ``
- bbox: `(661.1475830078125, 77.3359375) -> (710.8785400390625, 67.63577270507812)`
- raw_ref: `#/pictures/33`
- text/content preview: ``

### #/pictures/34
- type: `picture`
- order index: `167`
- page: `23`
- section title: ``
- section path: ``
- bbox: `(560.4761352539062, 48.8946533203125) -> (683.537109375, 16.38714599609375)`
- raw_ref: `#/pictures/34`
- text/content preview: ``

### #/texts/216
- type: `section_header`
- order index: `168`
- page: `24`
- section title: `Message transmission with FIFO (III)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (363.0155999999999, 463.77495071823205)`
- raw_ref: `#/texts/216`
- text/content preview: `Message transmission with FIFO (III)`

### #/texts/217
- type: `code`
- order index: `169`
- page: `24`
- section title: ``
- section path: ``
- bbox: `(108.67, 422.104) -> (678.6272399999999, 154.7974296182473)`
- raw_ref: `#/texts/217`
- text/content preview: `anz = strlen(msgbuf) + 1; write(fds, msgbuf, anz); printf ('Parent process: EXIT\ n'); } else { if ((fds=open(fifo_nam, O_RDONLY)) == -1) { printf ('Child process: Could't open FIFO for reading (%s)!\ n',strerror (errno)); return EXIT FAILURE; } printf ('Child process: Waiting for a message...\ n');`

### #/pictures/35
- type: `picture`
- order index: `170`
- page: `24`
- section title: ``
- section path: ``
- bbox: `(661.29150390625, 77.32452392578125) -> (710.911865234375, 67.64236450195312)`
- raw_ref: `#/pictures/35`
- text/content preview: ``

### #/pictures/36
- type: `picture`
- order index: `171`
- page: `24`
- section title: ``
- section path: ``
- bbox: `(560.5905151367188, 48.882232666015625) -> (683.4411010742188, 16.3636474609375)`
- raw_ref: `#/pictures/36`
- text/content preview: ``

### #/texts/219
- type: `text`
- order index: `172`
- page: `24`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/219`
- text/content preview: `DE`

### #/texts/224
- type: `section_header`
- order index: `173`
- page: `25`
- section title: `Message transmission with FIFO (IV)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (365.1271199999999, 463.77495071823205)`
- raw_ref: `#/texts/224`
- text/content preview: `Message transmission with FIFO (IV)`

### #/texts/225
- type: `code`
- order index: `174`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(108.67, 422.104) -> (667.8059999999998, 267.3974296182473)`
- raw_ref: `#/texts/225`
- text/content preview: `if ((anz=read(fds, msgbuf, sizeof(msgbuf))) != -1) { } else`

### #/texts/226
- type: `text`
- order index: `175`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(72.648, 197.37400000000002) -> (83.448, 183.12124129651863)`
- raw_ref: `#/texts/226`
- text/content preview: `}`

### #/texts/227
- type: `list_item`
- order index: `176`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(106.51, 253.55399999999997) -> (693.2879999999999, 70.68040458286987)`
- raw_ref: `#/texts/227`
- text/content preview: `n', → Properties of FIFOs: · for multiple processes · access via names, · definition at runtime, · still existing after program termination → Skat exercise using FIFOs!`

### #/texts/230
- type: `list_item`
- order index: `177`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(106.51, 78.28147200000001) -> (189.790672, 62.11523854143644)`
- raw_ref: `#/texts/230`
- text/content preview: `slower.`

### #/pictures/37
- type: `picture`
- order index: `178`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(661.1077880859375, 77.3323974609375) -> (710.8327026367188, 67.647216796875)`
- raw_ref: `#/pictures/37`
- text/content preview: ``

### #/pictures/38
- type: `picture`
- order index: `179`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(560.6327514648438, 48.858306884765625) -> (683.404541015625, 16.35595703125)`
- raw_ref: `#/pictures/38`
- text/content preview: ``

### #/texts/229
- type: `code`
- order index: `180`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(144.67, 394.039192) -> (660.8399999999999, 211.2174296182473)`
- raw_ref: `#/texts/229`
- text/content preview: `printf ('Child process: I received this message:\n %s\ n', msgbuf); remove(fifo_nam); printf ('Child process: EXIT\ n'); printf ('Child process: No message for me (%s)!\ strerror(errno));`

### #/texts/231
- type: `text`
- order index: `181`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(36.648, 169.069192) -> (47.4624, 154.7974296182473)`
- raw_ref: `#/texts/231`
- text/content preview: `}`

### #/texts/232
- type: `text`
- order index: `182`
- page: `25`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/232`
- text/content preview: `DE`

### #/texts/237
- type: `code`
- order index: `183`
- page: `26`
- section title: ``
- section path: ``
- bbox: `(36.648, 481.64176) -> (552.8199999999999, 188.93929281767953)`
- raw_ref: `#/texts/237`
- text/content preview: `mq_open() mqptr = mq_open(mq_name, oflag, rights, attrib); or mqptr = mq_open(mq_name, oflag); mqptr: Queue pointer mq_name: Name of the queue oflag: Access mode rights: Read- or write rights attrib: attributes of the queue`

### #/texts/238
- type: `text`
- order index: `184`
- page: `26`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/238`
- text/content preview: `DE`

### #/pictures/39
- type: `picture`
- order index: `185`
- page: `26`
- section title: ``
- section path: ``
- bbox: `(560.729736328125, 48.891265869140625) -> (683.2051391601562, 16.37371826171875)`
- raw_ref: `#/pictures/39`
- text/content preview: ``

### #/texts/242
- type: `section_header`
- order index: `186`
- page: `27`
- section title: `Message queues`
- section path: ``
- bbox: `(36.648, 529.18376) -> (147.74352000000002, 516.6985197790054)`
- raw_ref: `#/texts/242`
- text/content preview: `Message queues`

### #/texts/243
- type: `text`
- order index: `187`
- page: `27`
- section title: ``
- section path: ``
- bbox: `(36.648, 481.64176) -> (413.09000000000003, 273.21929281767956)`
- raw_ref: `#/texts/243`
- text/content preview: `mq_send () mq_send(mqptr, msg, msg_len, prio); mqptr: Queue pointer msg: Pointer to date to send msg_len: number of bytes to send Prio: Priority of the message`

### #/texts/244
- type: `text`
- order index: `188`
- page: `27`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/244`
- text/content preview: `DE`

### #/pictures/40
- type: `picture`
- order index: `189`
- page: `27`
- section title: ``
- section path: ``
- bbox: `(560.7994995117188, 48.84051513671875) -> (683.2029418945312, 16.43548583984375)`
- raw_ref: `#/pictures/40`
- text/content preview: ``

### #/texts/249
- type: `code`
- order index: `190`
- page: `28`
- section title: ``
- section path: ``
- bbox: `(36.648, 481.64176) -> (563.6199999999999, 245.1192928176796)`
- raw_ref: `#/texts/249`
- text/content preview: `mq_receive () size = mq_receive(mqptr, msg, msg_len, prio_ptr); size: size of the message in bytes mqptr: Queue pointer msg: Pointer to receive buffer msg_len: Size of receive buffer in bytes prio_ptr: Pointer to priority variable`

### #/pictures/41
- type: `picture`
- order index: `191`
- page: `28`
- section title: ``
- section path: ``
- bbox: `(560.8441772460938, 48.857025146484375) -> (683.24462890625, 16.41552734375)`
- raw_ref: `#/pictures/41`
- text/content preview: ``

### #/texts/250
- type: `text`
- order index: `192`
- page: `28`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/250`
- text/content preview: `DE`

### #/texts/255
- type: `section_header`
- order index: `193`
- page: `29`
- section title: `Message transmission with queues (I)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (372.16423999999995, 463.77495071823205)`
- raw_ref: `#/texts/255`
- text/content preview: `Message transmission with queues (I)`

### #/texts/256
- type: `code`
- order index: `194`
- page: `29`
- section title: ``
- section path: ``
- bbox: `(36.648, 453.616) -> (671.1744, 68.5892412965186)`
- raw_ref: `#/texts/256`
- text/content preview: `#include <stdio.h> #include <stdlib.h> #include <string.h> #include <unistd.h> #include <sys/stat.h> #include <mqueue.h> #include <errno.h> // Note (20200330): message queues are not implemented for // Ubuntu 18.04 in a Windows 10 subsystem! #define ZMAX 80 #define PRIO 0 #define MODE (S_IRUSR|S_IWUSR|S_IRGRP|S_IWGR...`

### #/texts/257
- type: `text`
- order index: `195`
- page: `29`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/257`
- text/content preview: `DE`

### #/pictures/42
- type: `picture`
- order index: `196`
- page: `29`
- section title: ``
- section path: ``
- bbox: `(649.2127075195312, 77.26364135742188) -> (710.7503662109375, 66.27664184570312)`
- raw_ref: `#/pictures/42`
- text/content preview: ``

### #/texts/258
- type: `text`
- order index: `197`
- page: `29`
- section title: ``
- section path: ``
- bbox: `(662.5, 75.29983199999998) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/258`
- text/content preview: `queues.c`

### #/pictures/43
- type: `picture`
- order index: `198`
- page: `29`
- section title: ``
- section path: ``
- bbox: `(560.5352783203125, 48.8726806640625) -> (683.3543090820312, 16.3607177734375)`
- raw_ref: `#/pictures/43`
- text/content preview: ``

### #/texts/263
- type: `section_header`
- order index: `199`
- page: `30`
- section title: `Message transmission with queues (II)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (377.70199999999994, 463.77495071823205)`
- raw_ref: `#/texts/263`
- text/content preview: `Message transmission with queues (II)`

### #/texts/264
- type: `code`
- order index: `200`
- page: `30`
- section title: ``
- section path: ``
- bbox: `(72.648, 428.344) -> (714.6199999999999, 161.0374296182473)`
- raw_ref: `#/texts/264`
- text/content preview: `npid = fork(); if (npid) { sleep(1); if ((tmq=mq open(tmq_name, O WRONLY)) == -1) { printf ('Parent process: Can't open %s\ n', tmq_name); return EXIT FAILURE; } printf ('Parent process: Please type a message:\ n'); fflush (stdin) ; scanf ('%[ˆ \ n]', msgbuf);`

### #/pictures/44
- type: `picture`
- order index: `201`
- page: `30`
- section title: ``
- section path: ``
- bbox: `(649.3964233398438, 77.20480346679688) -> (710.8788452148438, 66.29571533203125)`
- raw_ref: `#/pictures/44`
- text/content preview: ``

### #/texts/265
- type: `text`
- order index: `202`
- page: `30`
- section title: ``
- section path: ``
- bbox: `(650.02, 76.694184) -> (659.9118159999999, 70.68040458286987)`
- raw_ref: `#/texts/265`
- text/content preview: `→`

### #/texts/266
- type: `text`
- order index: `203`
- page: `30`
- section title: ``
- section path: ``
- bbox: `(662.5, 75.29983199999998) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/266`
- text/content preview: `queues.c`

### #/pictures/45
- type: `picture`
- order index: `204`
- page: `30`
- section title: ``
- section path: ``
- bbox: `(560.573974609375, 48.911895751953125) -> (683.4227905273438, 16.371826171875)`
- raw_ref: `#/pictures/45`
- text/content preview: ``

### #/texts/267
- type: `text`
- order index: `205`
- page: `30`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/267`
- text/content preview: `DE`

### #/texts/272
- type: `section_header`
- order index: `206`
- page: `31`
- section title: `Message transmission with queues (III)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (383.23975999999993, 463.77495071823205)`
- raw_ref: `#/texts/272`
- text/content preview: `Message transmission with queues (III)`

### #/texts/273
- type: `code`
- order index: `207`
- page: `31`
- section title: ``
- section path: ``
- bbox: `(72.648, 428.344) -> (714.6199999999999, 133.1712412965186)`
- raw_ref: `#/texts/273`
- text/content preview: `if (mq_send(tmq, msgbuf, sizeof(msgbuf),PRIO) == -1) { printf ('Parent process: %s is not accessible\ n', tmq_name); return EXIT FAILURE; } if (mq_close(tmq) == -1) { printf ('Parent process: Can't close %s\ n',tmq_name ); return EXIT FAILURE; } printf ('Parent process: EXIT\ n'); }`

### #/pictures/46
- type: `picture`
- order index: `208`
- page: `31`
- section title: ``
- section path: ``
- bbox: `(649.3850708007812, 77.23013305664062) -> (710.80810546875, 66.2847900390625)`
- raw_ref: `#/pictures/46`
- text/content preview: ``

### #/texts/274
- type: `text`
- order index: `209`
- page: `31`
- section title: ``
- section path: ``
- bbox: `(650.02, 76.694184) -> (659.9118159999999, 70.68040458286987)`
- raw_ref: `#/texts/274`
- text/content preview: `→`

### #/texts/275
- type: `text`
- order index: `210`
- page: `31`
- section title: ``
- section path: ``
- bbox: `(662.5, 75.29983199999998) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/275`
- text/content preview: `queues.c`

### #/pictures/47
- type: `picture`
- order index: `211`
- page: `31`
- section title: ``
- section path: ``
- bbox: `(560.632568359375, 48.896484375) -> (683.3761596679688, 16.322509765625)`
- raw_ref: `#/pictures/47`
- text/content preview: ``

### #/pictures/48
- type: `picture`
- order index: `212`
- page: `31`
- section title: ``
- section path: ``
- bbox: `(664.4959716796875, 522.0357971191406) -> (709.0614624023438, 493.4260940551758)`
- raw_ref: `#/pictures/48`
- text/content preview: ``

### #/texts/276
- type: `text`
- order index: `213`
- page: `31`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/276`
- text/content preview: `DE`

### #/texts/281
- type: `section_header`
- order index: `214`
- page: `32`
- section title: `Message transmission with queues (IV)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (385.3512799999999, 463.77495071823205)`
- raw_ref: `#/texts/281`
- text/content preview: `Message transmission with queues (IV)`

### #/texts/282
- type: `code`
- order index: `215`
- page: `32`
- section title: ``
- section path: ``
- bbox: `(72.648, 428.344) -> (682.4379999999993, 132.93124129651858)`
- raw_ref: `#/texts/282`
- text/content preview: `else { mqattr.mq maxmsg = 10; mqattr.mq msgsize = ZMAX; mqattr.mq flags = 0; if ((tmq=mq open(tmq_name, O CREAT|O RDWR, MODE, &mqattr)) == -1) { printf ('Child process: Can't create Message Queue %s\ n', tmq_name); return EXIT FAILURE; } printf ('Child process: Waiting for a message...\ n');`

### #/pictures/49
- type: `picture`
- order index: `216`
- page: `32`
- section title: ``
- section path: ``
- bbox: `(649.395751953125, 77.2490234375) -> (710.8671264648438, 66.29428100585938)`
- raw_ref: `#/pictures/49`
- text/content preview: ``

### #/texts/283
- type: `text`
- order index: `217`
- page: `32`
- section title: ``
- section path: ``
- bbox: `(650.02, 76.694184) -> (710.5624, 67.29928344777909)`
- raw_ref: `#/texts/283`
- text/content preview: `→ queues.c`

### #/pictures/50
- type: `picture`
- order index: `218`
- page: `32`
- section title: ``
- section path: ``
- bbox: `(560.6088256835938, 48.8636474609375) -> (683.3746337890625, 16.333984375)`
- raw_ref: `#/pictures/50`
- text/content preview: ``

### #/texts/284
- type: `text`
- order index: `219`
- page: `32`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/284`
- text/content preview: `DE`

### #/texts/289
- type: `section_header`
- order index: `220`
- page: `33`
- section title: `Message transmission with queues (V)`
- section path: ``
- bbox: `(36.648, 481.64176) -> (379.83343999999994, 463.77495071823205)`
- raw_ref: `#/texts/289`
- text/content preview: `Message transmission with queues (V)`

### #/texts/290
- type: `text`
- order index: `221`
- page: `33`
- section title: ``
- section path: ``
- bbox: `(36.648, 84.762) -> (47.448, 70.50924129651861)`
- raw_ref: `#/texts/290`
- text/content preview: `}`

### #/texts/291
- type: `list_item`
- order index: `222`
- page: `33`
- section title: ``
- section path: ``
- bbox: `(72.648, 450.229192) -> (711.0199919999999, 67.29928344777909)`
- raw_ref: `#/texts/291`
- text/content preview: `if((anz=mq_receive(tmq,msgbuf,sizeof(msgbuf),&prio))>0){ printf ('Child process: I received this message:\n %s\ n', msgbuf); printf ('Child process: EXIT\ n'); } else printf ('Child process: No message for me!\ n'); if (mq unlink(tmq_name) != 0) { printf ('Child process: Can't remove Message Queue %s (%s)\ n', tmq_n...`

### #/pictures/51
- type: `picture`
- order index: `223`
- page: `33`
- section title: ``
- section path: ``
- bbox: `(560.6221923828125, 48.86358642578125) -> (683.47412109375, 16.353271484375)`
- raw_ref: `#/pictures/51`
- text/content preview: ``

### #/texts/292
- type: `text`
- order index: `224`
- page: `33`
- section title: ``
- section path: ``
- bbox: `(661.94, 526.4) -> (710.4927600000001, 482.47999999999996)`
- raw_ref: `#/texts/292`
- text/content preview: `DE`

## Document Graph Summary
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- document title: `10 OS-BS 2020 Interprocess communication E`
- document type: `unknown`
- section count: `42`
- element count: `224`
- chunk count: `34`
- table asset count: `0`
- picture asset count: `52`

## Section Hierarchy Tree

- Betriebssysteme / Operating Systems Interprocess Communication
- Signals
- Signals
- Catching a signal with a signal handler (I)
- Catching a signal with a signal handler (II)
- Process synchronisation with a signal (I)
- Process synchronisation with a signal (II)
- Process synchronisation with a signal (III)
- Signals
- Basic signal handling
- Parameter:
- Signals
- Advanced signal handling (I)
- Function sigaction :
- Parameter:
- Advanced signal handling(II)
- New action:
- Signals
- Usage of signal sets (I)
- Usage of signal sets (II)
- Signals
- Usage of signal sets (III)
- Signals
- sigsetjmp() and siglongjump()
- Usage of sigsetjmp() and siglongjump() (I)
- Usage of sigsetjmp() and siglongjump() (II)
- Pipes and FIFOs
- Usage of pipes and FIFOs
- Message transmission with pipe() (I)
- Message transmission with pipe() (II)
- Message transmission with pipe() (III)
- → Skat exercise using pipes!
- Message transmission with FIFO (I)
- Message transmission with FIFO (II)
- Message transmission with FIFO (III)
- Message transmission with FIFO (IV)
- Message queues
- Message transmission with queues (I)
- Message transmission with queues (II)
- Message transmission with queues (III)
- Message transmission with queues (IV)
- Message transmission with queues (V)

## Sections

### sec_c4df79ff7cfd497ab4b449b30fbe17f5
- title: `Betriebssysteme / Operating Systems Interprocess Communication`
- parent section id: ``
- section path: `Betriebssysteme / Operating Systems Interprocess Communication`
- page_start/page_end: `1 -> 2`
- order_index: `1`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_d9f23f92684b40bd97b9a9f6f6a40dd5
- title: `Signals`
- parent section id: ``
- section path: `Signals`
- page_start/page_end: `2`
- order_index: `8`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_cecca34b2e064ffe93d1452741161296
- title: `Signals`
- parent section id: ``
- section path: `Signals`
- page_start/page_end: `2`
- order_index: `9`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_44a3c9ecabc546969d8f7b88ede0c76b
- title: `Catching a signal with a signal handler (I)`
- parent section id: ``
- section path: `Catching a signal with a signal handler (I)`
- page_start/page_end: `3`
- order_index: `15`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_05fb265a21674343a4783f38c17cd3e2
- title: `Catching a signal with a signal handler (II)`
- parent section id: ``
- section path: `Catching a signal with a signal handler (II)`
- page_start/page_end: `4`
- order_index: `20`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_46c910939cb740b2be3fe4086d68916f
- title: `Process synchronisation with a signal (I)`
- parent section id: ``
- section path: `Process synchronisation with a signal (I)`
- page_start/page_end: `5`
- order_index: `25`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_c8f3a3eed1474cd199d29681f77bbf51
- title: `Process synchronisation with a signal (II)`
- parent section id: ``
- section path: `Process synchronisation with a signal (II)`
- page_start/page_end: `6`
- order_index: `30`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_bdc45057720343d3a8a8798782761750
- title: `Process synchronisation with a signal (III)`
- parent section id: ``
- section path: `Process synchronisation with a signal (III)`
- page_start/page_end: `7`
- order_index: `36`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_de9f9be5c08d43a7b72e283afd08c2de
- title: `Signals`
- parent section id: ``
- section path: `Signals`
- page_start/page_end: `8`
- order_index: `40`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_2386bd95693142c98bb24b002b5ea542
- title: `Basic signal handling`
- parent section id: ``
- section path: `Basic signal handling`
- page_start/page_end: `8`
- order_index: `41`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_b98d2d11d8464eeb94f4130bb91573eb
- title: `Parameter:`
- parent section id: ``
- section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `43`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_e4246c61d6a9408c9000622aca0e8795
- title: `Signals`
- parent section id: ``
- section path: `Signals`
- page_start/page_end: `9`
- order_index: `51`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_9e69e62aefc64c728e8fffb9d1ff2336
- title: `Advanced signal handling (I)`
- parent section id: ``
- section path: `Advanced signal handling (I)`
- page_start/page_end: `9`
- order_index: `52`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_f3a1756ee8634c8a8e84210b4bd2b37c
- title: `Function sigaction :`
- parent section id: ``
- section path: `Function sigaction :`
- page_start/page_end: `9`
- order_index: `53`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_59068a803d3d409396aa4f6191a927b9
- title: `Parameter:`
- parent section id: ``
- section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `55`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_ef5e13e40e1248c483b130c502b80581
- title: `Advanced signal handling(II)`
- parent section id: ``
- section path: `Advanced signal handling(II)`
- page_start/page_end: `10`
- order_index: `65`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_2112efb76f954bb3bb7384be124286f7
- title: `New action:`
- parent section id: ``
- section path: `New action:`
- page_start/page_end: `10`
- order_index: `68`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_dc26d285348a44a6a72983632ed57a51
- title: `Signals`
- parent section id: ``
- section path: `Signals`
- page_start/page_end: `11`
- order_index: `82`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_b9e33db9a6534309af66e4377aed8f99
- title: `Usage of signal sets (I)`
- parent section id: ``
- section path: `Usage of signal sets (I)`
- page_start/page_end: `11`
- order_index: `83`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_0ffb2a4106f7417c901752c362b022c1
- title: `Usage of signal sets (II)`
- parent section id: ``
- section path: `Usage of signal sets (II)`
- page_start/page_end: `12`
- order_index: `90`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_0458d92ed6004fc78bac4c22a646a3af
- title: `Signals`
- parent section id: ``
- section path: `Signals`
- page_start/page_end: `13`
- order_index: `97`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_b54d5f6ef3c4478f8db65457b206357f
- title: `Usage of signal sets (III)`
- parent section id: ``
- section path: `Usage of signal sets (III)`
- page_start/page_end: `13`
- order_index: `98`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_1d13d74d441a43eb9281cbb1195abb4c
- title: `Signals`
- parent section id: ``
- section path: `Signals`
- page_start/page_end: `14`
- order_index: `105`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_2d400cc284694de7991fd7fc05e0cc01
- title: `sigsetjmp() and siglongjump()`
- parent section id: ``
- section path: `sigsetjmp() and siglongjump()`
- page_start/page_end: `15`
- order_index: `115`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_7f22433404d542c6b7ab89a82510f5ff
- title: `Usage of sigsetjmp() and siglongjump() (I)`
- parent section id: ``
- section path: `Usage of sigsetjmp() and siglongjump() (I)`
- page_start/page_end: `16`
- order_index: `119`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_17ce5634952e4e10945df10bf999ce01
- title: `Usage of sigsetjmp() and siglongjump() (II)`
- parent section id: ``
- section path: `Usage of sigsetjmp() and siglongjump() (II)`
- page_start/page_end: `17`
- order_index: `125`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_795ccdd667324992aa38dc43fe350456
- title: `Pipes and FIFOs`
- parent section id: ``
- section path: `Pipes and FIFOs`
- page_start/page_end: `18`
- order_index: `130`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_c1f1604a0df8471eb4e9f53461ca217a
- title: `Usage of pipes and FIFOs`
- parent section id: ``
- section path: `Usage of pipes and FIFOs`
- page_start/page_end: `18`
- order_index: `131`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_a5efa3c9b7f142198d1ebe0cb79f1e3c
- title: `Message transmission with pipe() (I)`
- parent section id: ``
- section path: `Message transmission with pipe() (I)`
- page_start/page_end: `19`
- order_index: `135`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_081486f83b944c3c92af129c398bae6e
- title: `Message transmission with pipe() (II)`
- parent section id: ``
- section path: `Message transmission with pipe() (II)`
- page_start/page_end: `20`
- order_index: `141`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_9bfa3e7ee3694b3bb23e54a9f2c13802
- title: `Message transmission with pipe() (III)`
- parent section id: ``
- section path: `Message transmission with pipe() (III)`
- page_start/page_end: `21`
- order_index: `148`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_a0ee34b913234d0eb1ea96119845e4f5
- title: `→ Skat exercise using pipes!`
- parent section id: ``
- section path: `→ Skat exercise using pipes!`
- page_start/page_end: `21`
- order_index: `152`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_b8f02bdfd98940ceb69ad949bf41e63a
- title: `Message transmission with FIFO (I)`
- parent section id: ``
- section path: `Message transmission with FIFO (I)`
- page_start/page_end: `22`
- order_index: `158`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_60e318b446a74782a1b0f477ea58ce7f
- title: `Message transmission with FIFO (II)`
- parent section id: ``
- section path: `Message transmission with FIFO (II)`
- page_start/page_end: `23`
- order_index: `163`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_965602c51251403c82df41a4223b956f
- title: `Message transmission with FIFO (III)`
- parent section id: ``
- section path: `Message transmission with FIFO (III)`
- page_start/page_end: `24`
- order_index: `168`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_f466fdce1d02460f90ae8e645bee15c9
- title: `Message transmission with FIFO (IV)`
- parent section id: ``
- section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25 -> 26`
- order_index: `173`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_ab4d09499ed1405dbf9c35493c1438e9
- title: `Message queues`
- parent section id: ``
- section path: `Message queues`
- page_start/page_end: `27 -> 28`
- order_index: `186`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_02c199472b404f388fdf746fffccbb94
- title: `Message transmission with queues (I)`
- parent section id: ``
- section path: `Message transmission with queues (I)`
- page_start/page_end: `29`
- order_index: `193`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_b95badf2d9b64c25afac003a2985f6a0
- title: `Message transmission with queues (II)`
- parent section id: ``
- section path: `Message transmission with queues (II)`
- page_start/page_end: `30`
- order_index: `199`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_b0251e72de794859a82c946c05c49ff7
- title: `Message transmission with queues (III)`
- parent section id: ``
- section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `206`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_508e7d87d35b42b2ac06a511d7931193
- title: `Message transmission with queues (IV)`
- parent section id: ``
- section path: `Message transmission with queues (IV)`
- page_start/page_end: `32`
- order_index: `214`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

### sec_f002b762055748c9b3602bd00d104487
- title: `Message transmission with queues (V)`
- parent section id: ``
- section path: `Message transmission with queues (V)`
- page_start/page_end: `33`
- order_index: `220`
- raw heading_level: `1`
- effective heading_level: `1`
- strategy: `default`

## Elements

### el_9015975d21cc4476bfc92102ed38717a
- type: `section_header`
- section id: `sec_c4df79ff7cfd497ab4b449b30fbe17f5`
- resolved section path: `Betriebssysteme / Operating Systems Interprocess Communication`
- page_start/page_end: `1`
- order_index: `1`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Betriebssysteme / Operating Systems Interprocess Communication`

### el_22e54f1f9b6c47cf96d6a1a7507e3aae
- type: `text`
- section id: `sec_c4df79ff7cfd497ab4b449b30fbe17f5`
- resolved section path: `Betriebssysteme / Operating Systems Interprocess Communication`
- page_start/page_end: `1`
- order_index: `2`
- effective heading_level: ``
- heading level source: ``
- text preview: `SS 2020`

### el_34e42a8613d1442a8c61461ee15ff3b9
- type: `text`
- section id: `sec_c4df79ff7cfd497ab4b449b30fbe17f5`
- resolved section path: `Betriebssysteme / Operating Systems Interprocess Communication`
- page_start/page_end: `1`
- order_index: `3`
- effective heading_level: ``
- heading level source: ``
- text preview: `Prof. Dr.-Ing. Holger Gräßner`

### el_531833bf5a4a40149f17028641f8bcc5
- type: `text`
- section id: `sec_c4df79ff7cfd497ab4b449b30fbe17f5`
- resolved section path: `Betriebssysteme / Operating Systems Interprocess Communication`
- page_start/page_end: `1`
- order_index: `4`
- effective heading_level: ``
- heading level source: ``
- text preview: `[10 OS-BS 2020 Interprocess communication.pptx]`

### el_08def1933440446fb7e6867f954f7218
- type: `picture`
- section id: `sec_c4df79ff7cfd497ab4b449b30fbe17f5`
- resolved section path: `Betriebssysteme / Operating Systems Interprocess Communication`
- page_start/page_end: `1`
- order_index: `5`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_cc5518dc33c143e29c55b749fd9ae459
- type: `text`
- section id: `sec_c4df79ff7cfd497ab4b449b30fbe17f5`
- resolved section path: `Betriebssysteme / Operating Systems Interprocess Communication`
- page_start/page_end: `2`
- order_index: `6`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_bbd3f2ffa6904aa8bcd4d704bd65f662
- type: `picture`
- section id: `sec_c4df79ff7cfd497ab4b449b30fbe17f5`
- resolved section path: `Betriebssysteme / Operating Systems Interprocess Communication`
- page_start/page_end: `2`
- order_index: `7`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_c4074c75ccb2474986b8aa3bf2285add
- type: `section_header`
- section id: `sec_d9f23f92684b40bd97b9a9f6f6a40dd5`
- resolved section path: `Signals`
- page_start/page_end: `2`
- order_index: `8`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Signals`

### el_ca7bc0cd940f4af68a7078f2501b7a7e
- type: `section_header`
- section id: `sec_cecca34b2e064ffe93d1452741161296`
- resolved section path: `Signals`
- page_start/page_end: `2`
- order_index: `9`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Signals`

### el_7865d8d0d64b4fe9858cd6a92b1ad8f6
- type: `text`
- section id: `sec_cecca34b2e064ffe93d1452741161296`
- resolved section path: `Signals`
- page_start/page_end: `2`
- order_index: `10`
- effective heading_level: ``
- heading level source: ``
- text preview: `signal occurs`

### el_5be6583e868e43ccb90ce315cfafda16
- type: `text`
- section id: `sec_cecca34b2e064ffe93d1452741161296`
- resolved section path: `Signals`
- page_start/page_end: `2`
- order_index: `11`
- effective heading_level: ``
- heading level source: ``
- text preview: `handler is called`

### el_0db48ad9591648428ce473dcf650b7ba
- type: `text`
- section id: `sec_cecca34b2e064ffe93d1452741161296`
- resolved section path: `Signals`
- page_start/page_end: `2`
- order_index: `12`
- effective heading_level: ``
- heading level source: ``
- text preview: `return`

### el_5e573cf35c754208a82dc47a018cd85d
- type: `text`
- section id: `sec_cecca34b2e064ffe93d1452741161296`
- resolved section path: `Signals`
- page_start/page_end: `2`
- order_index: `13`
- effective heading_level: ``
- heading level source: ``
- text preview: `Signal-Handler`

### el_f1ab579109f3411b9f4de91c1bb4db99
- type: `picture`
- section id: `sec_cecca34b2e064ffe93d1452741161296`
- resolved section path: `Signals`
- page_start/page_end: `2`
- order_index: `14`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_9696e7bab253453bb1c93d154e49777a
- type: `section_header`
- section id: `sec_44a3c9ecabc546969d8f7b88ede0c76b`
- resolved section path: `Catching a signal with a signal handler (I)`
- page_start/page_end: `3`
- order_index: `15`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Catching a signal with a signal handler (I)`

### el_838759aef7a14082a04226ee84053c44
- type: `code`
- section id: `sec_44a3c9ecabc546969d8f7b88ede0c76b`
- resolved section path: `Catching a signal with a signal handler (I)`
- page_start/page_end: `3`
- order_index: `16`
- effective heading_level: ``
- heading level source: ``
- text preview: `#include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration */ volatile sig atomic t flag = FALSE; int main() { signal(SIGINT,sigh); /* assign handler fuction */ printf ('Press ˆC t...`

### el_79f6298d4f7f4c73917de7fd534ef891
- type: `text`
- section id: `sec_44a3c9ecabc546969d8f7b88ede0c76b`
- resolved section path: `Catching a signal with a signal handler (I)`
- page_start/page_end: `3`
- order_index: `17`
- effective heading_level: ``
- heading level source: ``
- text preview: `→ signal_handler.c`

### el_2c77abe6be124b3db72d0810b8a0626b
- type: `picture`
- section id: `sec_44a3c9ecabc546969d8f7b88ede0c76b`
- resolved section path: `Catching a signal with a signal handler (I)`
- page_start/page_end: `3`
- order_index: `18`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_ab00e3f5b26144ed816b1adf7a2c674e
- type: `text`
- section id: `sec_44a3c9ecabc546969d8f7b88ede0c76b`
- resolved section path: `Catching a signal with a signal handler (I)`
- page_start/page_end: `3`
- order_index: `19`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_c275a7a9018341bc911ac4a59ce3c4a1
- type: `section_header`
- section id: `sec_05fb265a21674343a4783f38c17cd3e2`
- resolved section path: `Catching a signal with a signal handler (II)`
- page_start/page_end: `4`
- order_index: `20`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Catching a signal with a signal handler (II)`

### el_174e67d32f6f49e0899a1dd1330bea80
- type: `code`
- section id: `sec_05fb265a21674343a4783f38c17cd3e2`
- resolved section path: `Catching a signal with a signal handler (II)`
- page_start/page_end: `4`
- order_index: `21`
- effective heading_level: ``
- heading level source: ``
- text preview: `while (!flag) ; printf (' Program will be terminated!\ n'); return 0; } void sigh(int signum) { flag = TRUE; }`

### el_080723c311cc41d0b6947435cfdd8d2a
- type: `text`
- section id: `sec_05fb265a21674343a4783f38c17cd3e2`
- resolved section path: `Catching a signal with a signal handler (II)`
- page_start/page_end: `4`
- order_index: `22`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_1410f7e8a6a743f68abfc536118e62a9
- type: `text`
- section id: `sec_05fb265a21674343a4783f38c17cd3e2`
- resolved section path: `Catching a signal with a signal handler (II)`
- page_start/page_end: `4`
- order_index: `23`
- effective heading_level: ``
- heading level source: ``
- text preview: `→ signal_handler.c`

### el_20be676efb874e919f7bec722d2155b7
- type: `picture`
- section id: `sec_05fb265a21674343a4783f38c17cd3e2`
- resolved section path: `Catching a signal with a signal handler (II)`
- page_start/page_end: `4`
- order_index: `24`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_193d403980b8459e9630ab60dcf52749
- type: `section_header`
- section id: `sec_46c910939cb740b2be3fe4086d68916f`
- resolved section path: `Process synchronisation with a signal (I)`
- page_start/page_end: `5`
- order_index: `25`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Process synchronisation with a signal (I)`

### el_d027313591bf413f92cf4b2673ea32c1
- type: `code`
- section id: `sec_46c910939cb740b2be3fe4086d68916f`
- resolved section path: `Process synchronisation with a signal (I)`
- page_start/page_end: `5`
- order_index: `26`
- effective heading_level: ``
- heading level source: ``
- text preview: `#include <stdio.h> #include <signal.h> #include <unistd.h> #include <sys/wait.h> #include <sys/types.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration */ int main(void) { pid t npid; int status; npid = fork();`

### el_1d3e3e357fba4f86921358295215905a
- type: `text`
- section id: `sec_46c910939cb740b2be3fe4086d68916f`
- resolved section path: `Process synchronisation with a signal (I)`
- page_start/page_end: `5`
- order_index: `27`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_1db2b6f3666e487ebb69dee4717085b8
- type: `text`
- section id: `sec_46c910939cb740b2be3fe4086d68916f`
- resolved section path: `Process synchronisation with a signal (I)`
- page_start/page_end: `5`
- order_index: `28`
- effective heading_level: ``
- heading level source: ``
- text preview: `→ proc_sync_signal.c`

### el_b235577e694e4ffc87512d7859ccb36d
- type: `picture`
- section id: `sec_46c910939cb740b2be3fe4086d68916f`
- resolved section path: `Process synchronisation with a signal (I)`
- page_start/page_end: `5`
- order_index: `29`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_43e6166e1b3f47fba0efa6818bb14217
- type: `section_header`
- section id: `sec_c8f3a3eed1474cd199d29681f77bbf51`
- resolved section path: `Process synchronisation with a signal (II)`
- page_start/page_end: `6`
- order_index: `30`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Process synchronisation with a signal (II)`

### el_48136f8929304f39b106ff70ba249076
- type: `code`
- section id: `sec_c8f3a3eed1474cd199d29681f77bbf51`
- resolved section path: `Process synchronisation with a signal (II)`
- page_start/page_end: `6`
- order_index: `31`
- effective heading_level: ``
- heading level source: ``
- text preview: `if (npid) { printf ('Parent process: Press CR to send SIGUSR1 to child process!\ n'); getchar() ; kill (npid, SIGUSR1); /* send SIGUSR1 to child npid */ printf ('Parent process: SIGUSR1 has been send.\ n'); wait(&status); printf ('Parent...`

### el_20c548b211a847f19ea989f53898da1e
- type: `picture`
- section id: `sec_c8f3a3eed1474cd199d29681f77bbf51`
- resolved section path: `Process synchronisation with a signal (II)`
- page_start/page_end: `6`
- order_index: `32`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_465a31dbb68c4284aba8492e810e30f7
- type: `text`
- section id: `sec_c8f3a3eed1474cd199d29681f77bbf51`
- resolved section path: `Process synchronisation with a signal (II)`
- page_start/page_end: `6`
- order_index: `33`
- effective heading_level: ``
- heading level source: ``
- text preview: `→ proc_sync_signal.c`

### el_585d479efaac49d5806d6fb24256ce32
- type: `picture`
- section id: `sec_c8f3a3eed1474cd199d29681f77bbf51`
- resolved section path: `Process synchronisation with a signal (II)`
- page_start/page_end: `6`
- order_index: `34`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_9ba3a5c64f734c84bf247a2f8824240b
- type: `text`
- section id: `sec_c8f3a3eed1474cd199d29681f77bbf51`
- resolved section path: `Process synchronisation with a signal (II)`
- page_start/page_end: `6`
- order_index: `35`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_0ab7b167320c4fa99cc643e4c8594361
- type: `section_header`
- section id: `sec_bdc45057720343d3a8a8798782761750`
- resolved section path: `Process synchronisation with a signal (III)`
- page_start/page_end: `7`
- order_index: `36`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Process synchronisation with a signal (III)`

### el_1992e1a9d57d4fe6a9733d818cc5b7b8
- type: `code`
- section id: `sec_bdc45057720343d3a8a8798782761750`
- resolved section path: `Process synchronisation with a signal (III)`
- page_start/page_end: `7`
- order_index: `37`
- effective heading_level: ``
- heading level source: ``
- text preview: `else { printf ('Child process: Waiting for signal...\ n'); signal(SIGUSR1, sigh); /* assign SIGUSR1 to handler */ pause(); /* block until signal */ printf ('Child process: SIGUSR1 received! End in 1s\ n'); sleep(1); return 55; } } void s...`

### el_c5cc9bb5553a433c88e7c904004b0d7d
- type: `picture`
- section id: `sec_bdc45057720343d3a8a8798782761750`
- resolved section path: `Process synchronisation with a signal (III)`
- page_start/page_end: `7`
- order_index: `38`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_7cc435f5e6fc4f41894d4b9faf9f0884
- type: `text`
- section id: `sec_bdc45057720343d3a8a8798782761750`
- resolved section path: `Process synchronisation with a signal (III)`
- page_start/page_end: `7`
- order_index: `39`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_0a4bc5bf216b43e3917cdef1605b0ddd
- type: `section_header`
- section id: `sec_de9f9be5c08d43a7b72e283afd08c2de`
- resolved section path: `Signals`
- page_start/page_end: `8`
- order_index: `40`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Signals`

### el_f25e3b1d3cee4a33b966f0d343eaafe8
- type: `section_header`
- section id: `sec_2386bd95693142c98bb24b002b5ea542`
- resolved section path: `Basic signal handling`
- page_start/page_end: `8`
- order_index: `41`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Basic signal handling`

### el_384d4133e8944a33af49475c0243e2fc
- type: `code`
- section id: `sec_2386bd95693142c98bb24b002b5ea542`
- resolved section path: `Basic signal handling`
- page_start/page_end: `8`
- order_index: `42`
- effective heading_level: ``
- heading level source: ``
- text preview: `sighandler_t signal (int signum, sighandler_t action);`

### el_4f212331cd754b8b888956fd36a9fd00
- type: `section_header`
- section id: `sec_b98d2d11d8464eeb94f4130bb91573eb`
- resolved section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `43`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Parameter:`

### el_27391d5bdb25499bbaa12fc15bda8082
- type: `text`
- section id: `sec_b98d2d11d8464eeb94f4130bb91573eb`
- resolved section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `44`
- effective heading_level: ``
- heading level source: ``
- text preview: `signum : Signal to specify it's behaviour.`

### el_35ff132db97d4fefb85468c3ac8823f3
- type: `text`
- section id: `sec_b98d2d11d8464eeb94f4130bb91573eb`
- resolved section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `45`
- effective heading_level: ``
- heading level source: ``
- text preview: `action : New action:`

### el_ce728d15504c427fb8e0149779eae5e2
- type: `list_item`
- section id: `sec_b98d2d11d8464eeb94f4130bb91573eb`
- resolved section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `46`
- effective heading_level: ``
- heading level source: ``
- text preview: `-SIG_DFL : Default action for this signal.`

### el_f5b6b00f8f174afd92185a2f9030b6bb
- type: `list_item`
- section id: `sec_b98d2d11d8464eeb94f4130bb91573eb`
- resolved section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `47`
- effective heading_level: ``
- heading level source: ``
- text preview: `-SIG_IGN : Ignore this signal (not possible for SIGKILL or SIGSTOP ).`

### el_1923eca7786449fa874b7d5edef668c1
- type: `list_item`
- section id: `sec_b98d2d11d8464eeb94f4130bb91573eb`
- resolved section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `48`
- effective heading_level: ``
- heading level source: ``
- text preview: `-Adress of a signal handler function.`

### el_dbb706b505f7409d8401e5d23740bffb
- type: `picture`
- section id: `sec_b98d2d11d8464eeb94f4130bb91573eb`
- resolved section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `49`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_966454ce54794d52acd0ffd76c8125cf
- type: `text`
- section id: `sec_b98d2d11d8464eeb94f4130bb91573eb`
- resolved section path: `Parameter:`
- page_start/page_end: `8`
- order_index: `50`
- effective heading_level: ``
- heading level source: ``
- text preview: `E`

### el_5b42fa660cd841f2b32d9883493adb18
- type: `section_header`
- section id: `sec_e4246c61d6a9408c9000622aca0e8795`
- resolved section path: `Signals`
- page_start/page_end: `9`
- order_index: `51`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Signals`

### el_e518eb0a44fa46b4be87f32704ed062b
- type: `section_header`
- section id: `sec_9e69e62aefc64c728e8fffb9d1ff2336`
- resolved section path: `Advanced signal handling (I)`
- page_start/page_end: `9`
- order_index: `52`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Advanced signal handling (I)`

### el_b4aac24b83cd4633a0db8eda62ea7341
- type: `section_header`
- section id: `sec_f3a1756ee8634c8a8e84210b4bd2b37c`
- resolved section path: `Function sigaction :`
- page_start/page_end: `9`
- order_index: `53`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Function sigaction :`

### el_3e43ab056461434e9e1684af308a32d2
- type: `text`
- section id: `sec_f3a1756ee8634c8a8e84210b4bd2b37c`
- resolved section path: `Function sigaction :`
- page_start/page_end: `9`
- order_index: `54`
- effective heading_level: ``
- heading level source: ``
- text preview: `int sigaction (int signum, const struct sigaction *restrict action, struct sigaction *restrict old-action);`

### el_d5a1f890eff6490c849cf7727608505a
- type: `section_header`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `55`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Parameter:`

### el_d509b6745f6d4a33965ed174e48cfc96
- type: `list_item`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `56`
- effective heading_level: ``
- heading level source: ``
- text preview: `signum :`

### el_2d35abd6389d4e9492fac7fecdd8477f
- type: `text`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `57`
- effective heading_level: ``
- heading level source: ``
- text preview: `Signal to specify it's behaviour.`

### el_2e9f88125c3e4092aa9f6966f4ab5eda
- type: `list_item`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `58`
- effective heading_level: ``
- heading level source: ``
- text preview: `action : New action. NULL`

### el_dce48e8ffb334e319b2065eef213171b
- type: `text`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `59`
- effective heading_level: ``
- heading level source: ``
- text preview: `: No change of behaviour.`

### el_b93a48764b32465c89067526c0e1a4d1
- type: `list_item`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `60`
- effective heading_level: ``
- heading level source: ``
- text preview: `old-action : Get information about the current behaviour.`

### el_75c854dca36f46c7b9d6ff6252a0db9b
- type: `text`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `61`
- effective heading_level: ``
- heading level source: ``
- text preview: `NULL`

### el_5a973125407c4c36a6c9fba866608cea
- type: `text`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `62`
- effective heading_level: ``
- heading level source: ``
- text preview: `: No information required.`

### el_a8946e30e0b04bcaa97e839bcaf3679f
- type: `picture`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `63`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_d433e3e62f06450db29608cb857acecb
- type: `text`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- resolved section path: `Parameter:`
- page_start/page_end: `9`
- order_index: `64`
- effective heading_level: ``
- heading level source: ``
- text preview: `E`

### el_00eb5d98774145f1a13dd8ef186f3e38
- type: `section_header`
- section id: `sec_ef5e13e40e1248c483b130c502b80581`
- resolved section path: `Advanced signal handling(II)`
- page_start/page_end: `10`
- order_index: `65`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Advanced signal handling(II)`

### el_a709bf51a3d64b0bbdc0a90fadddf67b
- type: `text`
- section id: `sec_ef5e13e40e1248c483b130c502b80581`
- resolved section path: `Advanced signal handling(II)`
- page_start/page_end: `10`
- order_index: `66`
- effective heading_level: ``
- heading level source: ``
- text preview: `Structure sigaction with some elements:`

### el_29324fc3264440a4b2e98fb01f48a3a1
- type: `code`
- section id: `sec_ef5e13e40e1248c483b130c502b80581`
- resolved section path: `Advanced signal handling(II)`
- page_start/page_end: `10`
- order_index: `67`
- effective heading_level: ``
- heading level source: ``
- text preview: `sighandler_t sa_handler`

### el_dcd9aa8f69004989ba111462ebb915b3
- type: `section_header`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `68`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `New action:`

### el_573b7b6c56d94789a3ce745ea36883aa
- type: `list_item`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `69`
- effective heading_level: ``
- heading level source: ``
- text preview: `-SIG_DFL : Default action for this signal.`

### el_83db45dd6803461392a7aa31c871f5df
- type: `list_item`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `70`
- effective heading_level: ``
- heading level source: ``
- text preview: `-SIG_IGN : Ignore this signal (not possible for SIGKILL or SIGSTOP ).`

### el_40b0413f4c464d9a84af268e50a1211d
- type: `list_item`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `71`
- effective heading_level: ``
- heading level source: ``
- text preview: `-Handler : Adress of a signal handler function.`

### el_de046bb7e9bc4455989eb82e1c7c97bf
- type: `code`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `72`
- effective heading_level: ``
- heading level source: ``
- text preview: `sigset_t sa_mask :`

### el_8b525be5309f4078986919d638a5fc64
- type: `text`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `73`
- effective heading_level: ``
- heading level source: ``
- text preview: `Specifies a set of signals to block, while the handler is running.`

### el_bb0dfdd5f67b4677918806c00777ab9b
- type: `text`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `74`
- effective heading_level: ``
- heading level source: ``
- text preview: `Should be defined by usage of the functions sigemptyset() and sigaddset() , or sigfillset() and sigdelset() .`

### el_b24cc3f9f75f449698d6a63ad9b76dae
- type: `code`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `75`
- effective heading_level: ``
- heading level source: ``
- text preview: `int sa_flags :`

### el_ee35a5aabe3845a4b1d1a2ee7633de0a
- type: `text`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `76`
- effective heading_level: ``
- heading level source: ``
- text preview: `Flags to define the signal's behaviour:`

### el_48823c9b71d34c5ca25c8f95bfdb672b
- type: `list_item`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `77`
- effective heading_level: ``
- heading level source: ``
- text preview: `-e. g. SA_RESTART : Library functions like open() , read() , write()`

### el_4e003a32190649729eb3f6ef91749fa3
- type: `text`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `78`
- effective heading_level: ``
- heading level source: ``
- text preview: `will be resumed after execution of the signal handler.`

### el_cad3ee16778c4bb9ad2e35af6d0493d3
- type: `text`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `79`
- effective heading_level: ``
- heading level source: ``
- text preview: `-NULL : Library functions like open() , read() , write() ) will be terminated with errors after execution of the signal handler.`

### el_385671e5cb1a4a068fbed618ca7094b4
- type: `picture`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `80`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_054a3a2bb8a24b8e968e6a19c212162f
- type: `text`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- resolved section path: `New action:`
- page_start/page_end: `10`
- order_index: `81`
- effective heading_level: ``
- heading level source: ``
- text preview: `E`

### el_1fa95b69df37403281cc933e816e6681
- type: `section_header`
- section id: `sec_dc26d285348a44a6a72983632ed57a51`
- resolved section path: `Signals`
- page_start/page_end: `11`
- order_index: `82`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Signals`

### el_6b3f7e672ed94ef2ae55966326b01ec8
- type: `section_header`
- section id: `sec_b9e33db9a6534309af66e4377aed8f99`
- resolved section path: `Usage of signal sets (I)`
- page_start/page_end: `11`
- order_index: `83`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Usage of signal sets (I)`

### el_147fde79921d40b7860890406c9081ef
- type: `code`
- section id: `sec_b9e33db9a6534309af66e4377aed8f99`
- resolved section path: `Usage of signal sets (I)`
- page_start/page_end: `11`
- order_index: `84`
- effective heading_level: ``
- heading level source: ``
- text preview: `#include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) sig_atomic_t flag = FALSE; void sigh(int); int main() { sigset_t set; struct sigaction act;`

### el_15706a0cfb234443a8f00e8862390474
- type: `text`
- section id: `sec_b9e33db9a6534309af66e4377aed8f99`
- resolved section path: `Usage of signal sets (I)`
- page_start/page_end: `11`
- order_index: `85`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_3f53972e0e1245debb4d2fe6999395e6
- type: `picture`
- section id: `sec_b9e33db9a6534309af66e4377aed8f99`
- resolved section path: `Usage of signal sets (I)`
- page_start/page_end: `11`
- order_index: `86`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_f538fbebe4b1499ab25c64ab33c37d46
- type: `text`
- section id: `sec_b9e33db9a6534309af66e4377aed8f99`
- resolved section path: `Usage of signal sets (I)`
- page_start/page_end: `11`
- order_index: `87`
- effective heading_level: ``
- heading level source: ``
- text preview: `→`

### el_50933a4aabb2455faec28a01b20d411c
- type: `text`
- section id: `sec_b9e33db9a6534309af66e4377aed8f99`
- resolved section path: `Usage of signal sets (I)`
- page_start/page_end: `11`
- order_index: `88`
- effective heading_level: ``
- heading level source: ``
- text preview: `signal_set.c`

### el_a1af3dbd4e844097ab7e61a5b822975b
- type: `picture`
- section id: `sec_b9e33db9a6534309af66e4377aed8f99`
- resolved section path: `Usage of signal sets (I)`
- page_start/page_end: `11`
- order_index: `89`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_13d670e19b654c0cb7c0162c1fe39f47
- type: `section_header`
- section id: `sec_0ffb2a4106f7417c901752c362b022c1`
- resolved section path: `Usage of signal sets (II)`
- page_start/page_end: `12`
- order_index: `90`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Usage of signal sets (II)`

### el_b5650e02c1cf42d48f663744211c309a
- type: `code`
- section id: `sec_0ffb2a4106f7417c901752c362b022c1`
- resolved section path: `Usage of signal sets (II)`
- page_start/page_end: `12`
- order_index: `91`
- effective heading_level: ``
- heading level source: ``
- text preview: `sigemptyset(&set); sigaddset(&set, SIGINT); act.sa_flags = 0; act.sa_mask = set; act.sa_handler = &sigh; sigaction(SIGINT, &act, NULL); printf ('Press ˆC to call the signal handler!\ n'); while (!flag) ; printf ('Programm terminates now!...`

### el_98a64a563c6f4ca5b7b20536c4ce4a46
- type: `picture`
- section id: `sec_0ffb2a4106f7417c901752c362b022c1`
- resolved section path: `Usage of signal sets (II)`
- page_start/page_end: `12`
- order_index: `92`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_4b6fc35fe49247f1928a37b4fe96dfa4
- type: `text`
- section id: `sec_0ffb2a4106f7417c901752c362b022c1`
- resolved section path: `Usage of signal sets (II)`
- page_start/page_end: `12`
- order_index: `93`
- effective heading_level: ``
- heading level source: ``
- text preview: `→`

### el_de84449b5d17476f8d1d2dc65ebc4723
- type: `text`
- section id: `sec_0ffb2a4106f7417c901752c362b022c1`
- resolved section path: `Usage of signal sets (II)`
- page_start/page_end: `12`
- order_index: `94`
- effective heading_level: ``
- heading level source: ``
- text preview: `signal_set.c`

### el_594e6db3a51340eb823fdf523b548f0d
- type: `picture`
- section id: `sec_0ffb2a4106f7417c901752c362b022c1`
- resolved section path: `Usage of signal sets (II)`
- page_start/page_end: `12`
- order_index: `95`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_90b9a5fa5a574cf59db3e6b5fb99182a
- type: `text`
- section id: `sec_0ffb2a4106f7417c901752c362b022c1`
- resolved section path: `Usage of signal sets (II)`
- page_start/page_end: `12`
- order_index: `96`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_25275ace9e024378bc886ccfa63eba30
- type: `section_header`
- section id: `sec_0458d92ed6004fc78bac4c22a646a3af`
- resolved section path: `Signals`
- page_start/page_end: `13`
- order_index: `97`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Signals`

### el_515ccf44616949d1819b8452bbb6a243
- type: `section_header`
- section id: `sec_b54d5f6ef3c4478f8db65457b206357f`
- resolved section path: `Usage of signal sets (III)`
- page_start/page_end: `13`
- order_index: `98`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Usage of signal sets (III)`

### el_6f55419df4374ea58a897b2793dbb308
- type: `code`
- section id: `sec_b54d5f6ef3c4478f8db65457b206357f`
- resolved section path: `Usage of signal sets (III)`
- page_start/page_end: `13`
- order_index: `99`
- effective heading_level: ``
- heading level source: ``
- text preview: `void sigh(int signum) { flag = TRUE; }`

### el_a3887e51b34a49a79141c2cde9d35635
- type: `text`
- section id: `sec_b54d5f6ef3c4478f8db65457b206357f`
- resolved section path: `Usage of signal sets (III)`
- page_start/page_end: `13`
- order_index: `100`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_74091e1b6d1e4701a66c073f5905de4a
- type: `picture`
- section id: `sec_b54d5f6ef3c4478f8db65457b206357f`
- resolved section path: `Usage of signal sets (III)`
- page_start/page_end: `13`
- order_index: `101`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_d35b444e0c7c46bab6f8a438e24be63e
- type: `text`
- section id: `sec_b54d5f6ef3c4478f8db65457b206357f`
- resolved section path: `Usage of signal sets (III)`
- page_start/page_end: `13`
- order_index: `102`
- effective heading_level: ``
- heading level source: ``
- text preview: `→`

### el_a818b1bfcd5e44d586bd44493ce60480
- type: `text`
- section id: `sec_b54d5f6ef3c4478f8db65457b206357f`
- resolved section path: `Usage of signal sets (III)`
- page_start/page_end: `13`
- order_index: `103`
- effective heading_level: ``
- heading level source: ``
- text preview: `signal_set.c`

### el_618f2b6ded4844f3ad801148c34da416
- type: `picture`
- section id: `sec_b54d5f6ef3c4478f8db65457b206357f`
- resolved section path: `Usage of signal sets (III)`
- page_start/page_end: `13`
- order_index: `104`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_0d62d7c2e1f04efe890ce0cb8197e424
- type: `section_header`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `105`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Signals`

### el_28ae0b30e60b4c838ef59338b1049620
- type: `text`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `106`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_8c0c49c58b3c45b292acb35f45765d1c
- type: `picture`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `107`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_a877513a5bf747b99e062eb7ac24eafd
- type: `text`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `108`
- effective heading_level: ``
- heading level source: ``
- text preview: `sigsetjmp() siglongjump()`

### el_146478ca80b64b4e982e73b350ac5f56
- type: `text`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `109`
- effective heading_level: ``
- heading level source: ``
- text preview: `Define poit of reentry with sigsetjmp()`

### el_b210ebad4dca44b7973e8d21f8c87f84
- type: `text`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `110`
- effective heading_level: ``
- heading level source: ``
- text preview: `signal occurs`

### el_fbc27b2032dc45bf8a8be7e2c4a7339d
- type: `text`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `111`
- effective heading_level: ``
- heading level source: ``
- text preview: `Handler is called`

### el_1c84456c30444a35bea4b17fd14ca483
- type: `text`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `112`
- effective heading_level: ``
- heading level source: ``
- text preview: `jump to point of reentry with siglongjmp()`

### el_8abc902b60ec4410901dfc8236c08c9c
- type: `text`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `113`
- effective heading_level: ``
- heading level source: ``
- text preview: `Signal-Handler`

### el_9236b4f717ba44e5874d9038176929e2
- type: `picture`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- resolved section path: `Signals`
- page_start/page_end: `14`
- order_index: `114`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_f30f9a061cdc476eb62a9b35413efe62
- type: `section_header`
- section id: `sec_2d400cc284694de7991fd7fc05e0cc01`
- resolved section path: `sigsetjmp() and siglongjump()`
- page_start/page_end: `15`
- order_index: `115`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `sigsetjmp() and siglongjump()`

### el_55262c91d8e94c5f9f50a7f6f2920ee2
- type: `text`
- section id: `sec_2d400cc284694de7991fd7fc05e0cc01`
- resolved section path: `sigsetjmp() and siglongjump()`
- page_start/page_end: `15`
- order_index: `116`
- effective heading_level: ``
- heading level source: ``
- text preview: `sigsetjmp(env,smask); env: adress of environment buffer smask: ≠ 0: include signal mask Return value : = 0 : first call (definition of jump label) ≠ 0 : following calls (jump to label) siglongjmp(env,ret); env: adress of environment buff...`

### el_2b4c7dcc87f4452caeeae5181ae6a489
- type: `text`
- section id: `sec_2d400cc284694de7991fd7fc05e0cc01`
- resolved section path: `sigsetjmp() and siglongjump()`
- page_start/page_end: `15`
- order_index: `117`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_8f3885e24e99479686f850644d4053fe
- type: `picture`
- section id: `sec_2d400cc284694de7991fd7fc05e0cc01`
- resolved section path: `sigsetjmp() and siglongjump()`
- page_start/page_end: `15`
- order_index: `118`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_8aaa4f03b9fc41bf808cfdb52d3ca9c2
- type: `section_header`
- section id: `sec_7f22433404d542c6b7ab89a82510f5ff`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (I)`
- page_start/page_end: `16`
- order_index: `119`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Usage of sigsetjmp() and siglongjump() (I)`

### el_130fbd77943744058d77343bc6548203
- type: `code`
- section id: `sec_7f22433404d542c6b7ab89a82510f5ff`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (I)`
- page_start/page_end: `16`
- order_index: `120`
- effective heading_level: ``
- heading level source: ``
- text preview: `#include <stdio.h> #include <signal.h> #include <setjmp.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); Sigjmp_buf env; int main() { int retval; signal(SIGINT,sigh);`

### el_d9db9fe738b3480e9fb42c81ebc428e8
- type: `text`
- section id: `sec_7f22433404d542c6b7ab89a82510f5ff`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (I)`
- page_start/page_end: `16`
- order_index: `121`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_15d24fc9e490449c9a8971368c075efb
- type: `picture`
- section id: `sec_7f22433404d542c6b7ab89a82510f5ff`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (I)`
- page_start/page_end: `16`
- order_index: `122`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_d4d04c60b3f9426fa9465e21a930d946
- type: `text`
- section id: `sec_7f22433404d542c6b7ab89a82510f5ff`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (I)`
- page_start/page_end: `16`
- order_index: `123`
- effective heading_level: ``
- heading level source: ``
- text preview: `→ siglongjmp.c`

### el_4af9f2f5803d417fbe9d3dd37875eae0
- type: `picture`
- section id: `sec_7f22433404d542c6b7ab89a82510f5ff`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (I)`
- page_start/page_end: `16`
- order_index: `124`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_c5d027730eb04cb2a98f7e236cc529e8
- type: `section_header`
- section id: `sec_17ce5634952e4e10945df10bf999ce01`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (II)`
- page_start/page_end: `17`
- order_index: `125`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Usage of sigsetjmp() and siglongjump() (II)`

### el_4fc8e50f845a4d0aae5dc6cf99d39068
- type: `code`
- section id: `sec_17ce5634952e4e10945df10bf999ce01`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (II)`
- page_start/page_end: `17`
- order_index: `126`
- effective heading_level: ``
- heading level source: ``
- text preview: `if (( ret val = sigsetjmp(env,0)) == 0) {// first call printf (' sigsetjmp() has been initialised. Return value was %d.\n -> endless loop\ n', retval); while (1) ; } else // following calls printf ('Return value of sigsetjmp() was now %d...`

### el_37a0699447a94d91b64922883bdbcebb
- type: `text`
- section id: `sec_17ce5634952e4e10945df10bf999ce01`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (II)`
- page_start/page_end: `17`
- order_index: `127`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_c5821d9a7da740c2a6025935ad933817
- type: `text`
- section id: `sec_17ce5634952e4e10945df10bf999ce01`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (II)`
- page_start/page_end: `17`
- order_index: `128`
- effective heading_level: ``
- heading level source: ``
- text preview: `siglongjmp.c`

### el_04ab7845fc3e4dbb823d0544407915d8
- type: `picture`
- section id: `sec_17ce5634952e4e10945df10bf999ce01`
- resolved section path: `Usage of sigsetjmp() and siglongjump() (II)`
- page_start/page_end: `17`
- order_index: `129`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_5c269e76c1494591acf60d30900b7e38
- type: `section_header`
- section id: `sec_795ccdd667324992aa38dc43fe350456`
- resolved section path: `Pipes and FIFOs`
- page_start/page_end: `18`
- order_index: `130`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Pipes and FIFOs`

### el_a1daa12f95be4e07bd395d09d7a5fb82
- type: `section_header`
- section id: `sec_c1f1604a0df8471eb4e9f53461ca217a`
- resolved section path: `Usage of pipes and FIFOs`
- page_start/page_end: `18`
- order_index: `131`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Usage of pipes and FIFOs`

### el_2252e80bfa2744d08edb9c28b52491e5
- type: `code`
- section id: `sec_c1f1604a0df8471eb4e9f53461ca217a`
- resolved section path: `Usage of pipes and FIFOs`
- page_start/page_end: `18`
- order_index: `132`
- effective heading_level: ``
- heading level source: ``
- text preview: `int fds[2], rval; rval = pipe(fds); // create pipe write(fds [1], ...); // write access read(fds [0], ...) ; // read access int fds, rval ; rval = mkfifo(name,rights); // create FIFO fds = open(name,mode) // open FIFO write(fds, ...); //...`

### el_fa6ea01252834b71bd52337d2a16528b
- type: `text`
- section id: `sec_c1f1604a0df8471eb4e9f53461ca217a`
- resolved section path: `Usage of pipes and FIFOs`
- page_start/page_end: `18`
- order_index: `133`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_1fc27aa9d03d4d44b7cfc3cd64e220ed
- type: `picture`
- section id: `sec_c1f1604a0df8471eb4e9f53461ca217a`
- resolved section path: `Usage of pipes and FIFOs`
- page_start/page_end: `18`
- order_index: `134`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_f730a22239ff480ea9f29582989f1f91
- type: `section_header`
- section id: `sec_a5efa3c9b7f142198d1ebe0cb79f1e3c`
- resolved section path: `Message transmission with pipe() (I)`
- page_start/page_end: `19`
- order_index: `135`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with pipe() (I)`

### el_10c1e3f680344de7895b2e106da31500
- type: `code`
- section id: `sec_a5efa3c9b7f142198d1ebe0cb79f1e3c`
- resolved section path: `Message transmission with pipe() (I)`
- page_start/page_end: `19`
- order_index: `136`
- effective heading_level: ``
- heading level source: ``
- text preview: `#include <stdio.h> #include <stdlib.h> #include <sys/types.h> #include <sys/stat.h> #include <errno.h> int main(void) { pid_t npid; size_t anz; int fds[2]; char msgbuf [100]=' \ 0'; if (pipe(fds) < 0) { perror ('Pipe'); return EXIT FAILU...`

### el_e321423c93314c3fa4f4d8ddbd507beb
- type: `text`
- section id: `sec_a5efa3c9b7f142198d1ebe0cb79f1e3c`
- resolved section path: `Message transmission with pipe() (I)`
- page_start/page_end: `19`
- order_index: `137`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_459355a53cc74b5c9553922c49c61e32
- type: `picture`
- section id: `sec_a5efa3c9b7f142198d1ebe0cb79f1e3c`
- resolved section path: `Message transmission with pipe() (I)`
- page_start/page_end: `19`
- order_index: `138`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_385a5b49dcd44da8a67b95ad7971a2d2
- type: `text`
- section id: `sec_a5efa3c9b7f142198d1ebe0cb79f1e3c`
- resolved section path: `Message transmission with pipe() (I)`
- page_start/page_end: `19`
- order_index: `139`
- effective heading_level: ``
- heading level source: ``
- text preview: `→ pipe.c`

### el_6ff48510188f46c79690311f273bee6f
- type: `picture`
- section id: `sec_a5efa3c9b7f142198d1ebe0cb79f1e3c`
- resolved section path: `Message transmission with pipe() (I)`
- page_start/page_end: `19`
- order_index: `140`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_3229238996ab447cbb12c8e7fd2711ee
- type: `section_header`
- section id: `sec_081486f83b944c3c92af129c398bae6e`
- resolved section path: `Message transmission with pipe() (II)`
- page_start/page_end: `20`
- order_index: `141`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with pipe() (II)`

### el_c552d347a8154cc18afd5200ef35721c
- type: `code`
- section id: `sec_081486f83b944c3c92af129c398bae6e`
- resolved section path: `Message transmission with pipe() (II)`
- page_start/page_end: `20`
- order_index: `142`
- effective heading_level: ``
- heading level source: ``
- text preview: `npid = fork(); if (npid) { printf ('Parent process: please type a message:\ n'); fflush (stdin); scanf ('%[ˆ \ n]', msgbuf); anz = strlen (msgbuf)+1; write(fds[1], msgbuf, anz); printf ('Parent process: EXIT\ n'); }`

### el_8bb2fea042e24860937bdfc0536abf47
- type: `text`
- section id: `sec_081486f83b944c3c92af129c398bae6e`
- resolved section path: `Message transmission with pipe() (II)`
- page_start/page_end: `20`
- order_index: `143`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_1dc5f00d32f744428d5f926a51403cf6
- type: `picture`
- section id: `sec_081486f83b944c3c92af129c398bae6e`
- resolved section path: `Message transmission with pipe() (II)`
- page_start/page_end: `20`
- order_index: `144`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_126becfbd1f54e5688c1f6680a8f9c77
- type: `text`
- section id: `sec_081486f83b944c3c92af129c398bae6e`
- resolved section path: `Message transmission with pipe() (II)`
- page_start/page_end: `20`
- order_index: `145`
- effective heading_level: ``
- heading level source: ``
- text preview: `→`

### el_a256ce836fce4c239f8ef8d498fb1a9d
- type: `text`
- section id: `sec_081486f83b944c3c92af129c398bae6e`
- resolved section path: `Message transmission with pipe() (II)`
- page_start/page_end: `20`
- order_index: `146`
- effective heading_level: ``
- heading level source: ``
- text preview: `pipe.c`

### el_d5f5f34f65484bf1bdd6b0177f5c3bf3
- type: `picture`
- section id: `sec_081486f83b944c3c92af129c398bae6e`
- resolved section path: `Message transmission with pipe() (II)`
- page_start/page_end: `20`
- order_index: `147`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_6a117c8009be41d59f2b8faf4ab364cb
- type: `section_header`
- section id: `sec_9bfa3e7ee3694b3bb23e54a9f2c13802`
- resolved section path: `Message transmission with pipe() (III)`
- page_start/page_end: `21`
- order_index: `148`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with pipe() (III)`

### el_5f327db7c3ee4581a811f7bf21cfa566
- type: `text`
- section id: `sec_9bfa3e7ee3694b3bb23e54a9f2c13802`
- resolved section path: `Message transmission with pipe() (III)`
- page_start/page_end: `21`
- order_index: `149`
- effective heading_level: ``
- heading level source: ``
- text preview: `}`

### el_10744f4a25d3428aa9de5a3b97aa9ac6
- type: `code`
- section id: `sec_9bfa3e7ee3694b3bb23e54a9f2c13802`
- resolved section path: `Message transmission with pipe() (III)`
- page_start/page_end: `21`
- order_index: `150`
- effective heading_level: ``
- heading level source: ``
- text preview: `else { printf ('Child process: waiting for message...\ n'); if ((anz=read(fds[0], msgbuf, sizeof(msgbuf))) != -1) { printf ('Child process: I received this message: \n %s\ n', msgbuf); printf ('Child process: EXIT\ n'); } else printf ('C...`

### el_8d7a8e58fdf24d3c8cbab2ff93a4036e
- type: `list_item`
- section id: `sec_9bfa3e7ee3694b3bb23e54a9f2c13802`
- resolved section path: `Message transmission with pipe() (III)`
- page_start/page_end: `21`
- order_index: `151`
- effective heading_level: ``
- heading level source: ``
- text preview: `easy and fast.`

### el_d5d9e41cc55a4087a8f0958ad1c7368b
- type: `section_header`
- section id: `sec_a0ee34b913234d0eb1ea96119845e4f5`
- resolved section path: `→ Skat exercise using pipes!`
- page_start/page_end: `21`
- order_index: `152`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `→ Skat exercise using pipes!`

### el_fcfb10c6298d4953bee8f271e91cf820
- type: `text`
- section id: `sec_a0ee34b913234d0eb1ea96119845e4f5`
- resolved section path: `→ Skat exercise using pipes!`
- page_start/page_end: `21`
- order_index: `153`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_8ee965167c934e51be2ac4f826f605c6
- type: `picture`
- section id: `sec_a0ee34b913234d0eb1ea96119845e4f5`
- resolved section path: `→ Skat exercise using pipes!`
- page_start/page_end: `21`
- order_index: `154`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_cd33b4ab0ccc4f4291e8d6115506162e
- type: `text`
- section id: `sec_a0ee34b913234d0eb1ea96119845e4f5`
- resolved section path: `→ Skat exercise using pipes!`
- page_start/page_end: `21`
- order_index: `155`
- effective heading_level: ``
- heading level source: ``
- text preview: `→`

### el_d5d66ac712e64c219b0df6bdede33012
- type: `text`
- section id: `sec_a0ee34b913234d0eb1ea96119845e4f5`
- resolved section path: `→ Skat exercise using pipes!`
- page_start/page_end: `21`
- order_index: `156`
- effective heading_level: ``
- heading level source: ``
- text preview: `pipe.c`

### el_81f38bbeaa2649f28ae3a6f84402dd48
- type: `picture`
- section id: `sec_a0ee34b913234d0eb1ea96119845e4f5`
- resolved section path: `→ Skat exercise using pipes!`
- page_start/page_end: `21`
- order_index: `157`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_a98ebea2f386410cab9a68650b91ce0e
- type: `section_header`
- section id: `sec_b8f02bdfd98940ceb69ad949bf41e63a`
- resolved section path: `Message transmission with FIFO (I)`
- page_start/page_end: `22`
- order_index: `158`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with FIFO (I)`

### el_7e6257563765490da5243e04012f8ede
- type: `code`
- section id: `sec_b8f02bdfd98940ceb69ad949bf41e63a`
- resolved section path: `Message transmission with FIFO (I)`
- page_start/page_end: `22`
- order_index: `159`
- effective heading_level: ``
- heading level source: ``
- text preview: `#include <stdio.h> #include <stdlib.h> #include <sys/types.h> #include <sys/stat.h> #include <fcntl.h> #include <errno.h> // Note: FIFOs will not run on a Windows NTFS file system! #define TFIFO ' tfifo ' #define BUFLEN 100 #define MODE...`

### el_038812f61abf484faf26ca4123b473e5
- type: `picture`
- section id: `sec_b8f02bdfd98940ceb69ad949bf41e63a`
- resolved section path: `Message transmission with FIFO (I)`
- page_start/page_end: `22`
- order_index: `160`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_4897405921cc484f93180ed49f486698
- type: `picture`
- section id: `sec_b8f02bdfd98940ceb69ad949bf41e63a`
- resolved section path: `Message transmission with FIFO (I)`
- page_start/page_end: `22`
- order_index: `161`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_6d2287a44e8d42d7b05d34878aa43fd7
- type: `text`
- section id: `sec_b8f02bdfd98940ceb69ad949bf41e63a`
- resolved section path: `Message transmission with FIFO (I)`
- page_start/page_end: `22`
- order_index: `162`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_3d3dd8429e38458597f55953df083817
- type: `section_header`
- section id: `sec_60e318b446a74782a1b0f477ea58ce7f`
- resolved section path: `Message transmission with FIFO (II)`
- page_start/page_end: `23`
- order_index: `163`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with FIFO (II)`

### el_25c8e1e50df0486890de9394c99f691e
- type: `code`
- section id: `sec_60e318b446a74782a1b0f477ea58ce7f`
- resolved section path: `Message transmission with FIFO (II)`
- page_start/page_end: `23`
- order_index: `164`
- effective heading_level: ``
- heading level source: ``
- text preview: `if (mkfifo(fifo_nam, MODE) < 0) { printf ('Error creating FIFO (%s)!\ n', strerror(errno)); return EXIT FAILURE; } npid = fork(); if (npid) { if ((fds=open(fifo_nam, O_WRONLY)) == -1) { printf ('Parent process: Could't open FIFO for writ...`

### el_3fb5c4413e3b4ebd9954306d4d68154e
- type: `text`
- section id: `sec_60e318b446a74782a1b0f477ea58ce7f`
- resolved section path: `Message transmission with FIFO (II)`
- page_start/page_end: `23`
- order_index: `165`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_7f28263a3a934392bef717cbc4f262b7
- type: `picture`
- section id: `sec_60e318b446a74782a1b0f477ea58ce7f`
- resolved section path: `Message transmission with FIFO (II)`
- page_start/page_end: `23`
- order_index: `166`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_5b87244e93124d1389631c2699dca178
- type: `picture`
- section id: `sec_60e318b446a74782a1b0f477ea58ce7f`
- resolved section path: `Message transmission with FIFO (II)`
- page_start/page_end: `23`
- order_index: `167`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_03fa03325cbb457b8161cb5041f47fac
- type: `section_header`
- section id: `sec_965602c51251403c82df41a4223b956f`
- resolved section path: `Message transmission with FIFO (III)`
- page_start/page_end: `24`
- order_index: `168`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with FIFO (III)`

### el_e663277d7177499a8a2a9e6f7c5e7ff4
- type: `code`
- section id: `sec_965602c51251403c82df41a4223b956f`
- resolved section path: `Message transmission with FIFO (III)`
- page_start/page_end: `24`
- order_index: `169`
- effective heading_level: ``
- heading level source: ``
- text preview: `anz = strlen(msgbuf) + 1; write(fds, msgbuf, anz); printf ('Parent process: EXIT\ n'); } else { if ((fds=open(fifo_nam, O_RDONLY)) == -1) { printf ('Child process: Could't open FIFO for reading (%s)!\ n',strerror (errno)); return EXIT FA...`

### el_b1be064656284dad9423538eff887642
- type: `picture`
- section id: `sec_965602c51251403c82df41a4223b956f`
- resolved section path: `Message transmission with FIFO (III)`
- page_start/page_end: `24`
- order_index: `170`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_0d735cc400ef493aab095a4f7f0690bc
- type: `picture`
- section id: `sec_965602c51251403c82df41a4223b956f`
- resolved section path: `Message transmission with FIFO (III)`
- page_start/page_end: `24`
- order_index: `171`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_b1eec0a0b68349158f531db00b7d409e
- type: `text`
- section id: `sec_965602c51251403c82df41a4223b956f`
- resolved section path: `Message transmission with FIFO (III)`
- page_start/page_end: `24`
- order_index: `172`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_778c8e839f4b471f9a09aa9c793bf764
- type: `section_header`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `173`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with FIFO (IV)`

### el_f376ea6a778d4dadb7f5807d60241a2b
- type: `code`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `174`
- effective heading_level: ``
- heading level source: ``
- text preview: `if ((anz=read(fds, msgbuf, sizeof(msgbuf))) != -1) { } else`

### el_2489b820781748019cbf69000e7f093d
- type: `text`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `175`
- effective heading_level: ``
- heading level source: ``
- text preview: `}`

### el_d7af30ee7a954373bb72a0efd91797b7
- type: `list_item`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `176`
- effective heading_level: ``
- heading level source: ``
- text preview: `n', → Properties of FIFOs: · for multiple processes · access via names, · definition at runtime, · still existing after program termination → Skat exercise using FIFOs!`

### el_e9b51b5cc7044d038261491e4f4d7c47
- type: `list_item`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `177`
- effective heading_level: ``
- heading level source: ``
- text preview: `slower.`

### el_e88a84e7e5c64be39b29378decd0a803
- type: `picture`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `178`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_6c175002941042bc9538b7bcdcf0fa6b
- type: `picture`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `179`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_3ccf4ca9746d4d1a8ee244de3c74cf96
- type: `code`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `180`
- effective heading_level: ``
- heading level source: ``
- text preview: `printf ('Child process: I received this message:\n %s\ n', msgbuf); remove(fifo_nam); printf ('Child process: EXIT\ n'); printf ('Child process: No message for me (%s)!\ strerror(errno));`

### el_776921a6216f4318b95f3caa516b5403
- type: `text`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `181`
- effective heading_level: ``
- heading level source: ``
- text preview: `}`

### el_150c7111ab6e46a09e88fbf5451a4676
- type: `text`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `25`
- order_index: `182`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_8b11cf9c96fc40e8874847fc4ab92a98
- type: `code`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `26`
- order_index: `183`
- effective heading_level: ``
- heading level source: ``
- text preview: `mq_open() mqptr = mq_open(mq_name, oflag, rights, attrib); or mqptr = mq_open(mq_name, oflag); mqptr: Queue pointer mq_name: Name of the queue oflag: Access mode rights: Read- or write rights attrib: attributes of the queue`

### el_a5eb78cfe5db481cb692a14f0d5d2af3
- type: `text`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `26`
- order_index: `184`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_ef3e7ca332844264ba45e175c7f596c1
- type: `picture`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- resolved section path: `Message transmission with FIFO (IV)`
- page_start/page_end: `26`
- order_index: `185`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_37f0780bdd3b4287b994ee6298a35268
- type: `section_header`
- section id: `sec_ab4d09499ed1405dbf9c35493c1438e9`
- resolved section path: `Message queues`
- page_start/page_end: `27`
- order_index: `186`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message queues`

### el_bdb604de4568411eb5b3fbbe281f7d4b
- type: `text`
- section id: `sec_ab4d09499ed1405dbf9c35493c1438e9`
- resolved section path: `Message queues`
- page_start/page_end: `27`
- order_index: `187`
- effective heading_level: ``
- heading level source: ``
- text preview: `mq_send () mq_send(mqptr, msg, msg_len, prio); mqptr: Queue pointer msg: Pointer to date to send msg_len: number of bytes to send Prio: Priority of the message`

### el_8f0384a40e004a448008ebe87dac28ef
- type: `text`
- section id: `sec_ab4d09499ed1405dbf9c35493c1438e9`
- resolved section path: `Message queues`
- page_start/page_end: `27`
- order_index: `188`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_9b14249774da4a14b2ace4a2da5294f1
- type: `picture`
- section id: `sec_ab4d09499ed1405dbf9c35493c1438e9`
- resolved section path: `Message queues`
- page_start/page_end: `27`
- order_index: `189`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_0a5547a19fc543e482aef17af2a82ccb
- type: `code`
- section id: `sec_ab4d09499ed1405dbf9c35493c1438e9`
- resolved section path: `Message queues`
- page_start/page_end: `28`
- order_index: `190`
- effective heading_level: ``
- heading level source: ``
- text preview: `mq_receive () size = mq_receive(mqptr, msg, msg_len, prio_ptr); size: size of the message in bytes mqptr: Queue pointer msg: Pointer to receive buffer msg_len: Size of receive buffer in bytes prio_ptr: Pointer to priority variable`

### el_019e0660c1414cb8b60b5b7e97df5d7e
- type: `picture`
- section id: `sec_ab4d09499ed1405dbf9c35493c1438e9`
- resolved section path: `Message queues`
- page_start/page_end: `28`
- order_index: `191`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_7e8f5cdd56d140f1814871965ffcb2cf
- type: `text`
- section id: `sec_ab4d09499ed1405dbf9c35493c1438e9`
- resolved section path: `Message queues`
- page_start/page_end: `28`
- order_index: `192`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_9000febb095846c7802cefaa1a2a014e
- type: `section_header`
- section id: `sec_02c199472b404f388fdf746fffccbb94`
- resolved section path: `Message transmission with queues (I)`
- page_start/page_end: `29`
- order_index: `193`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with queues (I)`

### el_f18deee587954d6a8e13339b4ba9f905
- type: `code`
- section id: `sec_02c199472b404f388fdf746fffccbb94`
- resolved section path: `Message transmission with queues (I)`
- page_start/page_end: `29`
- order_index: `194`
- effective heading_level: ``
- heading level source: ``
- text preview: `#include <stdio.h> #include <stdlib.h> #include <string.h> #include <unistd.h> #include <sys/stat.h> #include <mqueue.h> #include <errno.h> // Note (20200330): message queues are not implemented for // Ubuntu 18.04 in a Windows 10 subsys...`

### el_c0ad942681d5424b999874db7cdaab73
- type: `text`
- section id: `sec_02c199472b404f388fdf746fffccbb94`
- resolved section path: `Message transmission with queues (I)`
- page_start/page_end: `29`
- order_index: `195`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_f477f76b4ff54f78907cf07527d9c18e
- type: `picture`
- section id: `sec_02c199472b404f388fdf746fffccbb94`
- resolved section path: `Message transmission with queues (I)`
- page_start/page_end: `29`
- order_index: `196`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_1546c53485094dd9b7dcdf2e6e8a83f0
- type: `text`
- section id: `sec_02c199472b404f388fdf746fffccbb94`
- resolved section path: `Message transmission with queues (I)`
- page_start/page_end: `29`
- order_index: `197`
- effective heading_level: ``
- heading level source: ``
- text preview: `queues.c`

### el_37d01befcf1045e5bc231746d2b161d1
- type: `picture`
- section id: `sec_02c199472b404f388fdf746fffccbb94`
- resolved section path: `Message transmission with queues (I)`
- page_start/page_end: `29`
- order_index: `198`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_2c7b59c886ee4e74a3151fa2e5eaf3e3
- type: `section_header`
- section id: `sec_b95badf2d9b64c25afac003a2985f6a0`
- resolved section path: `Message transmission with queues (II)`
- page_start/page_end: `30`
- order_index: `199`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with queues (II)`

### el_67f3200b318444a6b6515059cd3c6589
- type: `code`
- section id: `sec_b95badf2d9b64c25afac003a2985f6a0`
- resolved section path: `Message transmission with queues (II)`
- page_start/page_end: `30`
- order_index: `200`
- effective heading_level: ``
- heading level source: ``
- text preview: `npid = fork(); if (npid) { sleep(1); if ((tmq=mq open(tmq_name, O WRONLY)) == -1) { printf ('Parent process: Can't open %s\ n', tmq_name); return EXIT FAILURE; } printf ('Parent process: Please type a message:\ n'); fflush (stdin) ; scan...`

### el_af02736e08fc41ab8a377195952d864c
- type: `picture`
- section id: `sec_b95badf2d9b64c25afac003a2985f6a0`
- resolved section path: `Message transmission with queues (II)`
- page_start/page_end: `30`
- order_index: `201`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_51006f99a38a476b90dd3f1f83303377
- type: `text`
- section id: `sec_b95badf2d9b64c25afac003a2985f6a0`
- resolved section path: `Message transmission with queues (II)`
- page_start/page_end: `30`
- order_index: `202`
- effective heading_level: ``
- heading level source: ``
- text preview: `→`

### el_d38bda5d853c42849fcd874b2b709ffe
- type: `text`
- section id: `sec_b95badf2d9b64c25afac003a2985f6a0`
- resolved section path: `Message transmission with queues (II)`
- page_start/page_end: `30`
- order_index: `203`
- effective heading_level: ``
- heading level source: ``
- text preview: `queues.c`

### el_0b43555518774a32a98f59957e4d2d91
- type: `picture`
- section id: `sec_b95badf2d9b64c25afac003a2985f6a0`
- resolved section path: `Message transmission with queues (II)`
- page_start/page_end: `30`
- order_index: `204`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_a060e9d4b8d9465a9d2599df8dd7b68b
- type: `text`
- section id: `sec_b95badf2d9b64c25afac003a2985f6a0`
- resolved section path: `Message transmission with queues (II)`
- page_start/page_end: `30`
- order_index: `205`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_5dd65f0987384584b1aa45486a278f83
- type: `section_header`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- resolved section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `206`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with queues (III)`

### el_a5018ae80da6418c9a6a358580cfd8dc
- type: `code`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- resolved section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `207`
- effective heading_level: ``
- heading level source: ``
- text preview: `if (mq_send(tmq, msgbuf, sizeof(msgbuf),PRIO) == -1) { printf ('Parent process: %s is not accessible\ n', tmq_name); return EXIT FAILURE; } if (mq_close(tmq) == -1) { printf ('Parent process: Can't close %s\ n',tmq_name ); return EXIT FA...`

### el_cc215f988aa5436595c5dfc2ef3f15e8
- type: `picture`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- resolved section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `208`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_e9e017bb89df4019a15905ce133b668b
- type: `text`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- resolved section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `209`
- effective heading_level: ``
- heading level source: ``
- text preview: `→`

### el_ad3f3a686e1d45409cd674c7fc2d51d2
- type: `text`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- resolved section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `210`
- effective heading_level: ``
- heading level source: ``
- text preview: `queues.c`

### el_4d8f0a0316044e09820f862e4cb5e300
- type: `picture`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- resolved section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `211`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_9b1a9b88beec475cb4e1b6d701ca5440
- type: `picture`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- resolved section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `212`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_782c572aa882456db634a18e2df3f888
- type: `text`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- resolved section path: `Message transmission with queues (III)`
- page_start/page_end: `31`
- order_index: `213`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_f17e8bc28cfc4432b8a310f89334a755
- type: `section_header`
- section id: `sec_508e7d87d35b42b2ac06a511d7931193`
- resolved section path: `Message transmission with queues (IV)`
- page_start/page_end: `32`
- order_index: `214`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with queues (IV)`

### el_8e1b0a9e293b42ebb77ec9564a78b658
- type: `code`
- section id: `sec_508e7d87d35b42b2ac06a511d7931193`
- resolved section path: `Message transmission with queues (IV)`
- page_start/page_end: `32`
- order_index: `215`
- effective heading_level: ``
- heading level source: ``
- text preview: `else { mqattr.mq maxmsg = 10; mqattr.mq msgsize = ZMAX; mqattr.mq flags = 0; if ((tmq=mq open(tmq_name, O CREAT|O RDWR, MODE, &mqattr)) == -1) { printf ('Child process: Can't create Message Queue %s\ n', tmq_name); return EXIT FAILURE; }...`

### el_a108e0cf74c24a1e8d08d60d26ecb60d
- type: `picture`
- section id: `sec_508e7d87d35b42b2ac06a511d7931193`
- resolved section path: `Message transmission with queues (IV)`
- page_start/page_end: `32`
- order_index: `216`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_20a7350265084fe6a7a1de20bf50ceee
- type: `text`
- section id: `sec_508e7d87d35b42b2ac06a511d7931193`
- resolved section path: `Message transmission with queues (IV)`
- page_start/page_end: `32`
- order_index: `217`
- effective heading_level: ``
- heading level source: ``
- text preview: `→ queues.c`

### el_c783ee6779104844bf7c3ab16809e4e8
- type: `picture`
- section id: `sec_508e7d87d35b42b2ac06a511d7931193`
- resolved section path: `Message transmission with queues (IV)`
- page_start/page_end: `32`
- order_index: `218`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_da38f84ee2f547e8b0d1ac6c651f0d30
- type: `text`
- section id: `sec_508e7d87d35b42b2ac06a511d7931193`
- resolved section path: `Message transmission with queues (IV)`
- page_start/page_end: `32`
- order_index: `219`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

### el_171f21f85cb1469a968d750811db217e
- type: `section_header`
- section id: `sec_f002b762055748c9b3602bd00d104487`
- resolved section path: `Message transmission with queues (V)`
- page_start/page_end: `33`
- order_index: `220`
- effective heading_level: `1`
- heading level source: `default`
- text preview: `Message transmission with queues (V)`

### el_032146948ea74eb2bb8035d79b7deccd
- type: `text`
- section id: `sec_f002b762055748c9b3602bd00d104487`
- resolved section path: `Message transmission with queues (V)`
- page_start/page_end: `33`
- order_index: `221`
- effective heading_level: ``
- heading level source: ``
- text preview: `}`

### el_c12ffc0b27b44b6c9d1c44dcb4218b5c
- type: `list_item`
- section id: `sec_f002b762055748c9b3602bd00d104487`
- resolved section path: `Message transmission with queues (V)`
- page_start/page_end: `33`
- order_index: `222`
- effective heading_level: ``
- heading level source: ``
- text preview: `if((anz=mq_receive(tmq,msgbuf,sizeof(msgbuf),&prio))>0){ printf ('Child process: I received this message:\n %s\ n', msgbuf); printf ('Child process: EXIT\ n'); } else printf ('Child process: No message for me!\ n'); if (mq unlink(tmq_nam...`

### el_ecac012ebf3e4b9ba8d87193286d57c0
- type: `picture`
- section id: `sec_f002b762055748c9b3602bd00d104487`
- resolved section path: `Message transmission with queues (V)`
- page_start/page_end: `33`
- order_index: `223`
- effective heading_level: ``
- heading level source: ``
- text preview: ``

### el_d81cca62012645cc95f9db87696b31b5
- type: `text`
- section id: `sec_f002b762055748c9b3602bd00d104487`
- resolved section path: `Message transmission with queues (V)`
- page_start/page_end: `33`
- order_index: `224`
- effective heading_level: ``
- heading level source: ``
- text preview: `DE`

## Table Assets

_No table assets._

## Picture Assets

### picture_6b6637c8d64e462bbc5a439193d024c4
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_08def1933440446fb7e6867f954f7218`
- page_start/page_end: `1`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=1, page_end=1, bbox=BoundingBox(x1=486.7731628417969, y1=88.3543701171875, x2=683.4052124023438, y2=36.245635986328125)), caption=None, nearby_text=None)"
```

### picture_0eeea373e30143fcbafb1280c7a1d531
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_bbd3f2ffa6904aa8bcd4d704bd65f662`
- page_start/page_end: `2`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=2, page_end=2, bbox=BoundingBox(x1=32.33742141723633, y1=532.1867089271545, x2=667.2354736328125, y2=64.11972045898438)), caption=None, nearby_text=None)"
```

### picture_3972ee3687134f95aa7ba6d2dbbe90e5
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_f1ab579109f3411b9f4de91c1bb4db99`
- page_start/page_end: `2`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=2, page_end=2, bbox=BoundingBox(x1=560.805419921875, y1=49.137359619140625, x2=683.521240234375, y2=16.405029296875)), caption=None, nearby_text=None)"
```

### picture_bb60da52feeb476b8a1397935806fb21
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_2c77abe6be124b3db72d0810b8a0626b`
- page_start/page_end: `3`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=3, page_end=3, bbox=BoundingBox(x1=560.6714477539062, y1=48.936859130859375, x2=683.48779296875, y2=16.345703125)), caption=None, nearby_text=None)"
```

### picture_fcb1d047415748dc9c5304dbd8867109
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_20be676efb874e919f7bec722d2155b7`
- page_start/page_end: `4`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=4, page_end=4, bbox=BoundingBox(x1=560.7781372070312, y1=48.928131103515625, x2=683.4304809570312, y2=16.3720703125)), caption=None, nearby_text=None)"
```

### picture_15c27e51d69e4692aea9abc1855abf28
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_b235577e694e4ffc87512d7859ccb36d`
- page_start/page_end: `5`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=5, page_end=5, bbox=BoundingBox(x1=560.6431884765625, y1=48.949737548828125, x2=683.483642578125, y2=16.42071533203125)), caption=None, nearby_text=None)"
```

### picture_98b6ed18c5c842629ea668e7b8ce2349
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_20c548b211a847f19ea989f53898da1e`
- page_start/page_end: `6`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=6, page_end=6, bbox=BoundingBox(x1=588.8361206054688, y1=77.61093139648438, x2=710.9244995117188, y2=65.33694458007812)), caption=None, nearby_text=None)"
```

### picture_b3f3c4a6ef164ffca59706cb5220ba3f
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_585d479efaac49d5806d6fb24256ce32`
- page_start/page_end: `6`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=6, page_end=6, bbox=BoundingBox(x1=560.6157836914062, y1=48.907379150390625, x2=683.4541625976562, y2=16.37677001953125)), caption=None, nearby_text=None)"
```

### picture_f1987615ecc44cf490358bc4fe367ec9
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_c5cc9bb5553a433c88e7c904004b0d7d`
- page_start/page_end: `7`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=7, page_end=7, bbox=BoundingBox(x1=560.4451904296875, y1=49.04803466796875, x2=683.5855102539062, y2=16.3685302734375)), caption=None, nearby_text=None)"
```

### picture_319b98402dbe4015add5f5f0e7daba48
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_dbb706b505f7409d8401e5d23740bffb`
- page_start/page_end: `8`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=8, page_end=8, bbox=BoundingBox(x1=560.7848510742188, y1=48.889617919921875, x2=683.1738891601562, y2=16.360107421875)), caption=None, nearby_text=None)"
```

### picture_15ac3dc57b344a478c3bf0e25df8382b
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_a8946e30e0b04bcaa97e839bcaf3679f`
- page_start/page_end: `9`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=9, page_end=9, bbox=BoundingBox(x1=560.7531127929688, y1=48.820037841796875, x2=683.1976318359375, y2=16.430908203125)), caption=None, nearby_text=None)"
```

### picture_f8617a179c4540c08b63bbaa6dcd913d
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_385671e5cb1a4a068fbed618ca7094b4`
- page_start/page_end: `10`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=10, page_end=10, bbox=BoundingBox(x1=560.699462890625, y1=48.846343994140625, x2=683.1425170898438, y2=16.43304443359375)), caption=None, nearby_text=None)"
```

### picture_5187f6b9dd14487c9fd786e229173f96
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_3f53972e0e1245debb4d2fe6999395e6`
- page_start/page_end: `11`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=11, page_end=11, bbox=BoundingBox(x1=625.2288208007812, y1=77.70004272460938, x2=710.9901123046875, y2=64.43295288085938)), caption=None, nearby_text=None)"
```

### picture_03f17f2ab81e4bb09206d0363f83f168
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_a1af3dbd4e844097ab7e61a5b822975b`
- page_start/page_end: `11`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=11, page_end=11, bbox=BoundingBox(x1=560.740478515625, y1=48.841583251953125, x2=683.4296875, y2=16.3922119140625)), caption=None, nearby_text=None)"
```

### picture_917248544fb144bd9022fc9fca1650da
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_98a64a563c6f4ca5b7b20536c4ce4a46`
- page_start/page_end: `12`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=12, page_end=12, bbox=BoundingBox(x1=625.1753540039062, y1=77.68136596679688, x2=710.925048828125, y2=64.50106811523438)), caption=None, nearby_text=None)"
```

### picture_59b9ca9301fb4143b0dc9408c57c5713
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_594e6db3a51340eb823fdf523b548f0d`
- page_start/page_end: `12`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=12, page_end=12, bbox=BoundingBox(x1=560.6299438476562, y1=48.868621826171875, x2=683.3995971679688, y2=16.3658447265625)), caption=None, nearby_text=None)"
```

### picture_418461a47dd54a3892a82925d2c33029
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_74091e1b6d1e4701a66c073f5905de4a`
- page_start/page_end: `13`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=13, page_end=13, bbox=BoundingBox(x1=625.3656616210938, y1=77.67584228515625, x2=710.96337890625, y2=64.2947998046875)), caption=None, nearby_text=None)"
```

### picture_91511dac3a024f9ab88dd5538b9bc997
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_618f2b6ded4844f3ad801148c34da416`
- page_start/page_end: `13`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=13, page_end=13, bbox=BoundingBox(x1=560.8382568359375, y1=48.85980224609375, x2=683.3323974609375, y2=16.3985595703125)), caption=None, nearby_text=None)"
```

### picture_684a7e491fe34cac8cdc69fa058bc0e8
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_8c0c49c58b3c45b292acb35f45765d1c`
- page_start/page_end: `14`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=14, page_end=14, bbox=BoundingBox(x1=34.33107376098633, y1=521.909122467041, x2=685.432861328125, y2=62.417236328125)), caption=None, nearby_text=None)"
```

### picture_df27ec0ca41841d0b27b0876327f7322
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_9236b4f717ba44e5874d9038176929e2`
- page_start/page_end: `14`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=14, page_end=14, bbox=BoundingBox(x1=560.9716186523438, y1=49.09503173828125, x2=683.40283203125, y2=16.4447021484375)), caption=None, nearby_text=None)"
```

### picture_6135e4c72ca842bb9203a95d5a6eb579
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_8f3885e24e99479686f850644d4053fe`
- page_start/page_end: `15`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=15, page_end=15, bbox=BoundingBox(x1=560.844970703125, y1=48.84344482421875, x2=683.1758422851562, y2=16.4356689453125)), caption=None, nearby_text=None)"
```

### picture_28028bf446d9404489425885a38be25d
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_15d24fc9e490449c9a8971368c075efb`
- page_start/page_end: `16`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=16, page_end=16, bbox=BoundingBox(x1=625.2733154296875, y1=77.71163940429688, x2=710.8555908203125, y2=65.19207763671875)), caption=None, nearby_text=None)"
```

### picture_5899422885624861a2246e3561b8b9f6
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_4af9f2f5803d417fbe9d3dd37875eae0`
- page_start/page_end: `16`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=16, page_end=16, bbox=BoundingBox(x1=560.7233276367188, y1=48.85955810546875, x2=683.3724975585938, y2=16.36785888671875)), caption=None, nearby_text=None)"
```

### picture_0c6138930b8642b8ae2e8178bc27e1a9
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_04ab7845fc3e4dbb823d0544407915d8`
- page_start/page_end: `17`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=17, page_end=17, bbox=BoundingBox(x1=560.612548828125, y1=48.942169189453125, x2=683.4868774414062, y2=16.27960205078125)), caption=None, nearby_text=None)"
```

### picture_75846d8f756241318f9e6d4ba4f31bdb
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_1fc27aa9d03d4d44b7cfc3cd64e220ed`
- page_start/page_end: `18`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=18, page_end=18, bbox=BoundingBox(x1=560.6564331054688, y1=48.912750244140625, x2=683.2906494140625, y2=16.4149169921875)), caption=None, nearby_text=None)"
```

### picture_482f6a3ca18847fd8101c39198695aa2
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_459355a53cc74b5c9553922c49c61e32`
- page_start/page_end: `19`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=19, page_end=19, bbox=BoundingBox(x1=661.056884765625, y1=77.65426635742188, x2=710.8728637695312, y2=65.43826293945312)), caption=None, nearby_text=None)"
```

### picture_d9315cd8b2474c299e70a546bbc1f925
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_6ff48510188f46c79690311f273bee6f`
- page_start/page_end: `19`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=19, page_end=19, bbox=BoundingBox(x1=560.5835571289062, y1=48.89166259765625, x2=683.3668823242188, y2=16.40643310546875)), caption=None, nearby_text=None)"
```

### picture_191dc92078a345bda3640ef320ab6c08
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_1dc5f00d32f744428d5f926a51403cf6`
- page_start/page_end: `20`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=20, page_end=20, bbox=BoundingBox(x1=661.283935546875, y1=77.59860229492188, x2=710.9486083984375, y2=65.44003295898438)), caption=None, nearby_text=None)"
```

### picture_2add9933281646548d0088cb88c17a8a
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_d5f5f34f65484bf1bdd6b0177f5c3bf3`
- page_start/page_end: `20`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=20, page_end=20, bbox=BoundingBox(x1=560.729248046875, y1=48.869720458984375, x2=683.471435546875, y2=16.40240478515625)), caption=None, nearby_text=None)"
```

### picture_db5ba9e62b124eb08860097a88c9f100
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_8ee965167c934e51be2ac4f826f605c6`
- page_start/page_end: `21`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=21, page_end=21, bbox=BoundingBox(x1=661.0276489257812, y1=77.69424438476562, x2=710.9013671875, y2=65.3553466796875)), caption=None, nearby_text=None)"
```

### picture_31b91e293e1945c697f8953e813968bd
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_81f38bbeaa2649f28ae3a6f84402dd48`
- page_start/page_end: `21`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=21, page_end=21, bbox=BoundingBox(x1=560.6783447265625, y1=48.89697265625, x2=683.409912109375, y2=16.3321533203125)), caption=None, nearby_text=None)"
```

### picture_a0f8f88b08c74a0ca220d9ea7585f41c
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_038812f61abf484faf26ca4123b473e5`
- page_start/page_end: `22`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=22, page_end=22, bbox=BoundingBox(x1=661.271484375, y1=77.329833984375, x2=710.8663330078125, y2=67.65499877929688)), caption=None, nearby_text=None)"
```

### picture_167e765905be4f439ae6eb5e524fa9f7
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_4897405921cc484f93180ed49f486698`
- page_start/page_end: `22`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=22, page_end=22, bbox=BoundingBox(x1=560.60986328125, y1=48.871917724609375, x2=683.364501953125, y2=16.3936767578125)), caption=None, nearby_text=None)"
```

### picture_75c793e214024effb327cb21851ac965
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_7f28263a3a934392bef717cbc4f262b7`
- page_start/page_end: `23`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=23, page_end=23, bbox=BoundingBox(x1=661.1475830078125, y1=77.3359375, x2=710.8785400390625, y2=67.63577270507812)), caption=None, nearby_text=None)"
```

### picture_e9cb069bdc584b31ac868174698d2962
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_5b87244e93124d1389631c2699dca178`
- page_start/page_end: `23`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=23, page_end=23, bbox=BoundingBox(x1=560.4761352539062, y1=48.8946533203125, x2=683.537109375, y2=16.38714599609375)), caption=None, nearby_text=None)"
```

### picture_9a23b15f2dd840c792e35ba73f63c758
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_b1be064656284dad9423538eff887642`
- page_start/page_end: `24`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=24, page_end=24, bbox=BoundingBox(x1=661.29150390625, y1=77.32452392578125, x2=710.911865234375, y2=67.64236450195312)), caption=None, nearby_text=None)"
```

### picture_e52e871c60d44ebaac26fd1002c10fae
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_0d735cc400ef493aab095a4f7f0690bc`
- page_start/page_end: `24`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=24, page_end=24, bbox=BoundingBox(x1=560.5905151367188, y1=48.882232666015625, x2=683.4411010742188, y2=16.3636474609375)), caption=None, nearby_text=None)"
```

### picture_62647c872d2d40968fec018f56ea09fa
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_e88a84e7e5c64be39b29378decd0a803`
- page_start/page_end: `25`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=25, page_end=25, bbox=BoundingBox(x1=661.1077880859375, y1=77.3323974609375, x2=710.8327026367188, y2=67.647216796875)), caption=None, nearby_text=None)"
```

### picture_a125875cfe604e2984d965d325b058a4
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_6c175002941042bc9538b7bcdcf0fa6b`
- page_start/page_end: `25`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=25, page_end=25, bbox=BoundingBox(x1=560.6327514648438, y1=48.858306884765625, x2=683.404541015625, y2=16.35595703125)), caption=None, nearby_text=None)"
```

### picture_f1b05f2ff2af496a8fab3d5f54b936b6
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_ef3e7ca332844264ba45e175c7f596c1`
- page_start/page_end: `26`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=26, page_end=26, bbox=BoundingBox(x1=560.729736328125, y1=48.891265869140625, x2=683.2051391601562, y2=16.37371826171875)), caption=None, nearby_text=None)"
```

### picture_cf8a463badac4f3e9230078ad7cfd00f
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_9b14249774da4a14b2ace4a2da5294f1`
- page_start/page_end: `27`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=27, page_end=27, bbox=BoundingBox(x1=560.7994995117188, y1=48.84051513671875, x2=683.2029418945312, y2=16.43548583984375)), caption=None, nearby_text=None)"
```

### picture_9e05386a4d164e89b1cd94ab5c3d0d70
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_019e0660c1414cb8b60b5b7e97df5d7e`
- page_start/page_end: `28`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=28, page_end=28, bbox=BoundingBox(x1=560.8441772460938, y1=48.857025146484375, x2=683.24462890625, y2=16.41552734375)), caption=None, nearby_text=None)"
```

### picture_7fea48c08e8a4ae4b92cde57af86b90d
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_f477f76b4ff54f78907cf07527d9c18e`
- page_start/page_end: `29`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=29, page_end=29, bbox=BoundingBox(x1=649.2127075195312, y1=77.26364135742188, x2=710.7503662109375, y2=66.27664184570312)), caption=None, nearby_text=None)"
```

### picture_6cd613fd124b46aaa36d5b00878afc0a
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_37d01befcf1045e5bc231746d2b161d1`
- page_start/page_end: `29`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=29, page_end=29, bbox=BoundingBox(x1=560.5352783203125, y1=48.8726806640625, x2=683.3543090820312, y2=16.3607177734375)), caption=None, nearby_text=None)"
```

### picture_481cfd2e5c414308838a81a074c03cba
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_af02736e08fc41ab8a377195952d864c`
- page_start/page_end: `30`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=30, page_end=30, bbox=BoundingBox(x1=649.3964233398438, y1=77.20480346679688, x2=710.8788452148438, y2=66.29571533203125)), caption=None, nearby_text=None)"
```

### picture_91770d3a32ec4f538c49caad053a06e4
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_0b43555518774a32a98f59957e4d2d91`
- page_start/page_end: `30`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=30, page_end=30, bbox=BoundingBox(x1=560.573974609375, y1=48.911895751953125, x2=683.4227905273438, y2=16.371826171875)), caption=None, nearby_text=None)"
```

### picture_3274548f4c884c51ab64198b6630fb70
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_cc215f988aa5436595c5dfc2ef3f15e8`
- page_start/page_end: `31`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=31, page_end=31, bbox=BoundingBox(x1=649.3850708007812, y1=77.23013305664062, x2=710.80810546875, y2=66.2847900390625)), caption=None, nearby_text=None)"
```

### picture_c1783f0823a640479772bb32aff05659
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_4d8f0a0316044e09820f862e4cb5e300`
- page_start/page_end: `31`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=31, page_end=31, bbox=BoundingBox(x1=560.632568359375, y1=48.896484375, x2=683.3761596679688, y2=16.322509765625)), caption=None, nearby_text=None)"
```

### picture_ec5b71dd911e4fdba16e12b73f7d0a67
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_9b1a9b88beec475cb4e1b6d701ca5440`
- page_start/page_end: `31`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=31, page_end=31, bbox=BoundingBox(x1=664.4959716796875, y1=522.0357971191406, x2=709.0614624023438, y2=493.4260940551758)), caption=None, nearby_text=None)"
```

### picture_afd139dc832a468595803bff38ac49b8
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_a108e0cf74c24a1e8d08d60d26ecb60d`
- page_start/page_end: `32`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=32, page_end=32, bbox=BoundingBox(x1=649.395751953125, y1=77.2490234375, x2=710.8671264648438, y2=66.29428100585938)), caption=None, nearby_text=None)"
```

### picture_39158e82312d49d7b468697ada96b04e
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_c783ee6779104844bf7c3ab16809e4e8`
- page_start/page_end: `32`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=32, page_end=32, bbox=BoundingBox(x1=560.6088256835938, y1=48.8636474609375, x2=683.3746337890625, y2=16.333984375)), caption=None, nearby_text=None)"
```

### picture_e93c9febe277469b81622e12a8b0336a
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- element id: `el_ecac012ebf3e4b9ba8d87193286d57c0`
- page_start/page_end: `33`
- image path: ``
- caption/text: ``
- metadata:
```json
"AssetMetadata(source=SourceLocation(page_start=33, page_end=33, bbox=BoundingBox(x1=560.6221923828125, y1=48.86358642578125, x2=683.47412109375, y2=16.353271484375)), caption=None, nearby_text=None)"
```

## Chunks

### Chunk Summary
| sequence | chunk_id | section_id | section_path | chunk_pos | elements | pages | content preview |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | chunk_910999b297234ec6ad2ebb442ff83b5b | sec_c4df79ff7cfd497ab4b449b30fbe17f5 | Betriebssysteme / Operating Systems Interprocess Communication | 1/1 | 4 | 1 -> 2 | SS 2020 Prof. Dr.-Ing. Holger Gräßner [10 OS-BS 2020 Interprocess communication.pptx] DE |
| 2 | chunk_897c4f43339e416385ada7f4de39a9e4 | sec_44a3c9ecabc546969d8f7b88ede0c76b | Catching a signal with a signal handler (I) | 1/1 | 3 | 3 | #include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration *... |
| 3 | chunk_5af08587dac94fb39fdc1b82df167357 | sec_05fb265a21674343a4783f38c17cd3e2 | Catching a signal with a signal handler (II) | 1/1 | 3 | 4 | while (!flag) ; printf (' Program will be terminated!\ n'); return 0; } void sigh(int signum) { flag = TRUE; } DE → s... |
| 4 | chunk_1805d67970b24dd7aaa2c3d6ae9faad8 | sec_46c910939cb740b2be3fe4086d68916f | Process synchronisation with a signal (I) | 1/1 | 3 | 5 | #include <stdio.h> #include <signal.h> #include <unistd.h> #include <sys/wait.h> #include <sys/types.h> #define FALSE... |
| 5 | chunk_1f95805736034319bf57b6f283b7c620 | sec_c8f3a3eed1474cd199d29681f77bbf51 | Process synchronisation with a signal (II) | 1/1 | 2 | 6 | if (npid) { printf ('Parent process: Press CR to send SIGUSR1 to child process!\ n'); getchar() ; kill (npid, SIGUSR1... |
| 6 | chunk_bcdefcca8033441e9d4306353250e8e1 | sec_bdc45057720343d3a8a8798782761750 | Process synchronisation with a signal (III) | 1/1 | 2 | 7 | else { printf ('Child process: Waiting for signal...\ n'); signal(SIGUSR1, sigh); /* assign SIGUSR1 to handler */ pau... |
| 7 | chunk_9efce806f05d447985d413c1b79bfefd | sec_2386bd95693142c98bb24b002b5ea542 | Basic signal handling | 1/1 | 1 | 8 | sighandler_t signal (int signum, sighandler_t action); |
| 8 | chunk_de6a2ccecb43488b8903fd3e189d159c | sec_59068a803d3d409396aa4f6191a927b9 | Parameter: | 1/2 | 6 | 8 | signum : Signal to specify it's behaviour. action : New action: -SIG_DFL : Default action for this signal. -SIG_IGN :... |
| 9 | chunk_a410dedc107d45daa4f9ac198187890f | sec_f3a1756ee8634c8a8e84210b4bd2b37c | Function sigaction : | 1/1 | 1 | 9 | int sigaction (int signum, const struct sigaction *restrict action, struct sigaction *restrict old-action); |
| 10 | chunk_c24b2d31c6b547309362d4056e3830a4 | sec_59068a803d3d409396aa4f6191a927b9 | Parameter: | 2/2 | 8 | 9 | signum : Signal to specify it's behaviour. action : New action. NULL : No change of behaviour. old-action : Get infor... |
| 11 | chunk_34554e1003f14130b3ce190d4250431f | sec_ef5e13e40e1248c483b130c502b80581 | Advanced signal handling(II) | 1/1 | 2 | 10 | Structure sigaction with some elements: sighandler_t sa_handler |
| 12 | chunk_9db5f709433547e897fbea9d3e309834 | sec_2112efb76f954bb3bb7384be124286f7 | New action: | 1/1 | 12 | 10 | -SIG_DFL : Default action for this signal. -SIG_IGN : Ignore this signal (not possible for SIGKILL or SIGSTOP ). -Han... |
| 13 | chunk_1f3bc99528ac4a2196fe71c0dab71742 | sec_b9e33db9a6534309af66e4377aed8f99 | Usage of signal sets (I) | 1/1 | 2 | 11 | #include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) sig_atomic_t flag = FALSE; void sigh(int... |
| 14 | chunk_a8a0823deebb4cd98ca752ca34ae7237 | sec_0ffb2a4106f7417c901752c362b022c1 | Usage of signal sets (II) | 1/1 | 2 | 12 | sigemptyset(&set); sigaddset(&set, SIGINT); act.sa_flags = 0; act.sa_mask = set; act.sa_handler = &sigh; sigaction(SI... |
| 15 | chunk_401047cc49ab4f9caca90c41923b3897 | sec_b54d5f6ef3c4478f8db65457b206357f | Usage of signal sets (III) | 1/1 | 2 | 13 | void sigh(int signum) { flag = TRUE; } DE |
| 16 | chunk_78abfed34cb844aaaccc3837b51fe768 | sec_1d13d74d441a43eb9281cbb1195abb4c | Signals | 1/1 | 1 | 14 | DE |
| 17 | chunk_f65945faad1a4fa0994ddd4292881a41 | sec_2d400cc284694de7991fd7fc05e0cc01 | sigsetjmp() and siglongjump() | 1/1 | 2 | 15 | sigsetjmp(env,smask); env: adress of environment buffer smask: ≠ 0: include signal mask Return value : = 0 : first ca... |
| 18 | chunk_96f7afccf64445aab2609255cea6f477 | sec_7f22433404d542c6b7ab89a82510f5ff | Usage of sigsetjmp() and siglongjump() (I) | 1/1 | 2 | 16 | #include <stdio.h> #include <signal.h> #include <setjmp.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); Sigj... |
| 19 | chunk_270c3ad6bd7b4db5b8614ad5b08bc9f7 | sec_17ce5634952e4e10945df10bf999ce01 | Usage of sigsetjmp() and siglongjump() (II) | 1/1 | 3 | 17 | if (( ret val = sigsetjmp(env,0)) == 0) {// first call printf (' sigsetjmp() has been initialised. Return value was %... |
| 20 | chunk_bce32097d71f4f2983c73009d41e85ec | sec_c1f1604a0df8471eb4e9f53461ca217a | Usage of pipes and FIFOs | 1/1 | 2 | 18 | int fds[2], rval; rval = pipe(fds); // create pipe write(fds [1], ...); // write access read(fds [0], ...) ; // read... |

### chunk_910999b297234ec6ad2ebb442ff83b5b
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_c4df79ff7cfd497ab4b449b30fbe17f5`
- sequence_number: `1`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `1 -> 2`
- token_count: `12`
- section_path: `Betriebssysteme / Operating Systems Interprocess Communication`
- element_ids (4): `el_22e54f1f9b6c47cf96d6a1a7507e3aae, el_34e42a8613d1442a8c61461ee15ff3b9, el_531833bf5a4a40149f17028641f8bcc5, el_cc5518dc33c143e29c55b749fd9ae459`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Betriebssysteme / Operating Systems Interprocess Communication SS 2020 Prof. Dr.-Ing. Holger Gräßner [10 OS-BS 2020 Interprocess communication.pptx] DE`
- content:
```text
SS 2020

Prof. Dr.-Ing. Holger Gräßner

[10 OS-BS 2020 Interprocess communication.pptx]

DE
```

### chunk_897c4f43339e416385ada7f4de39a9e4
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_44a3c9ecabc546969d8f7b88ede0c76b`
- sequence_number: `2`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `3`
- token_count: `45`
- section_path: `Catching a signal with a signal handler (I)`
- element_ids (3): `el_838759aef7a14082a04226ee84053c44, el_79f6298d4f7f4c73917de7fd534ef891, el_ab00e3f5b26144ed816b1adf7a2c674e`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Catching a signal with a signal handler (I) #include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration */ v...`
- content:
```text
#include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration */ volatile sig atomic t flag = FALSE; int main() { signal(SIGINT,sigh); /* assign handler fuction */ printf ('Press ˆC to call the signal handler \ n');

→ signal_handler.c

DE
```

### chunk_5af08587dac94fb39fdc1b82df167357
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_05fb265a21674343a4783f38c17cd3e2`
- sequence_number: `3`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `4`
- token_count: `24`
- section_path: `Catching a signal with a signal handler (II)`
- element_ids (3): `el_174e67d32f6f49e0899a1dd1330bea80, el_080723c311cc41d0b6947435cfdd8d2a, el_1410f7e8a6a743f68abfc536118e62a9`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Catching a signal with a signal handler (II) while (!flag) ; printf (' Program will be terminated!\ n'); return 0; } void sigh(int signum) { flag = TRUE; } DE → sig...`
- content:
```text
while (!flag) ; printf (' Program will be terminated!\ n'); return 0; } void sigh(int signum) { flag = TRUE; }

DE

→ signal_handler.c
```

### chunk_1805d67970b24dd7aaa2c3d6ae9faad8
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_46c910939cb740b2be3fe4086d68916f`
- sequence_number: `4`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `5`
- token_count: `36`
- section_path: `Process synchronisation with a signal (I)`
- element_ids (3): `el_d027313591bf413f92cf4b2673ea32c1, el_1d3e3e357fba4f86921358295215905a, el_1db2b6f3666e487ebb69dee4717085b8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Process synchronisation with a signal (I) #include <stdio.h> #include <signal.h> #include <unistd.h> #include <sys/wait.h> #include <sys/types.h> #define FALSE 0 #d...`
- content:
```text
#include <stdio.h> #include <signal.h> #include <unistd.h> #include <sys/wait.h> #include <sys/types.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); /* handler declaration */ int main(void) { pid t npid; int status; npid = fork();

DE

→ proc_sync_signal.c
```

### chunk_1f95805736034319bf57b6f283b7c620
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_c8f3a3eed1474cd199d29681f77bbf51`
- sequence_number: `5`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `6`
- token_count: `53`
- section_path: `Process synchronisation with a signal (II)`
- element_ids (2): `el_48136f8929304f39b106ff70ba249076, el_9ba3a5c64f734c84bf247a2f8824240b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Process synchronisation with a signal (II) if (npid) { printf ('Parent process: Press CR to send SIGUSR1 to child process!\ n'); getchar() ; kill (npid, SIGUSR1); /...`
- content:
```text
if (npid) { printf ('Parent process: Press CR to send SIGUSR1 to child process!\ n'); getchar() ; kill (npid, SIGUSR1); /* send SIGUSR1 to child npid */ printf ('Parent process: SIGUSR1 has been send.\ n'); wait(&status); printf ('Parent process: Child process terminated, exit state = %i\ n', WEXITSTATUS( status)); return 0; }

DE
```

### chunk_bcdefcca8033441e9d4306353250e8e1
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_bdc45057720343d3a8a8798782761750`
- sequence_number: `6`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `7`
- token_count: `59`
- section_path: `Process synchronisation with a signal (III)`
- element_ids (2): `el_1992e1a9d57d4fe6a9733d818cc5b7b8, el_7cc435f5e6fc4f41894d4b9faf9f0884`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Process synchronisation with a signal (III) else { printf ('Child process: Waiting for signal...\ n'); signal(SIGUSR1, sigh); /* assign SIGUSR1 to handler */ pause(...`
- content:
```text
else { printf ('Child process: Waiting for signal...\ n'); signal(SIGUSR1, sigh); /* assign SIGUSR1 to handler */ pause(); /* block until signal */ printf ('Child process: SIGUSR1 received! End in 1s\ n'); sleep(1); return 55; } } void sigh(int signum) /* Signal handler for SIGUSR1 */ { /* attention: only reentrant resistant functions here... */ } → proc_sync_signal.c

DE
```

### chunk_9efce806f05d447985d413c1b79bfefd
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_2386bd95693142c98bb24b002b5ea542`
- sequence_number: `7`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `8`
- token_count: `6`
- section_path: `Basic signal handling`
- element_ids (1): `el_384d4133e8944a33af49475c0243e2fc`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Basic signal handling sighandler_t signal (int signum, sighandler_t action);`
- content:
```text
sighandler_t signal (int signum, sighandler_t action);
```

### chunk_de6a2ccecb43488b8903fd3e189d159c
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- sequence_number: `8`
- chunk_index/chunk_total: `1/2`
- chunk type: `general`
- page_start/page_end: `8`
- token_count: `37`
- section_path: `Parameter:`
- element_ids (6): `el_27391d5bdb25499bbaa12fc15bda8082, el_35ff132db97d4fefb85468c3ac8823f3, el_ce728d15504c427fb8e0149779eae5e2, el_f5b6b00f8f174afd92185a2f9030b6bb, el_1923eca7786449fa874b7d5edef668c1, el_966454ce54794d52acd0ffd76c8125cf`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Parameter: signum : Signal to specify it's behaviour. action : New action: -SIG_DFL : Default action for this signal. -SIG_IGN : Ignore this signal (not possible fo...`
- content:
```text
signum : Signal to specify it's behaviour.

action : New action:

-SIG_DFL : Default action for this signal.

-SIG_IGN : Ignore this signal (not possible for SIGKILL or SIGSTOP ).

-Adress of a signal handler function.

E
```

### chunk_a410dedc107d45daa4f9ac198187890f
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_f3a1756ee8634c8a8e84210b4bd2b37c`
- sequence_number: `9`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `9`
- token_count: `13`
- section_path: `Function sigaction :`
- element_ids (1): `el_3e43ab056461434e9e1684af308a32d2`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Function sigaction : int sigaction (int signum, const struct sigaction *restrict action, struct sigaction *restrict old-action);`
- content:
```text
int sigaction (int signum, const struct sigaction *restrict action, struct sigaction *restrict old-action);
```

### chunk_c24b2d31c6b547309362d4056e3830a4
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_59068a803d3d409396aa4f6191a927b9`
- sequence_number: `10`
- chunk_index/chunk_total: `2/2`
- chunk type: `general`
- page_start/page_end: `9`
- token_count: `31`
- section_path: `Parameter:`
- element_ids (8): `el_d509b6745f6d4a33965ed174e48cfc96, el_2d35abd6389d4e9492fac7fecdd8477f, el_2e9f88125c3e4092aa9f6966f4ab5eda, el_dce48e8ffb334e319b2065eef213171b, el_b93a48764b32465c89067526c0e1a4d1, el_75c854dca36f46c7b9d6ff6252a0db9b, el_5a973125407c4c36a6c9fba866608cea, el_d433e3e62f06450db29608cb857acecb`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Parameter: signum : Signal to specify it's behaviour. action : New action. NULL : No change of behaviour. old-action : Get information about the current behaviour....`
- content:
```text
signum :

Signal to specify it's behaviour.

action : New action. NULL

: No change of behaviour.

old-action : Get information about the current behaviour.

NULL

: No information required.

E
```

### chunk_34554e1003f14130b3ce190d4250431f
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_ef5e13e40e1248c483b130c502b80581`
- sequence_number: `11`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `10`
- token_count: `7`
- section_path: `Advanced signal handling(II)`
- element_ids (2): `el_a709bf51a3d64b0bbdc0a90fadddf67b, el_29324fc3264440a4b2e98fb01f48a3a1`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Advanced signal handling(II) Structure sigaction with some elements: sighandler_t sa_handler`
- content:
```text
Structure sigaction with some elements:

sighandler_t sa_handler
```

### chunk_9db5f709433547e897fbea9d3e309834
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_2112efb76f954bb3bb7384be124286f7`
- sequence_number: `12`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `10`
- token_count: `112`
- section_path: `New action:`
- element_ids (12): `el_573b7b6c56d94789a3ce745ea36883aa, el_83db45dd6803461392a7aa31c871f5df, el_40b0413f4c464d9a84af268e50a1211d, el_de046bb7e9bc4455989eb82e1c7c97bf, el_8b525be5309f4078986919d638a5fc64, el_bb0dfdd5f67b4677918806c00777ab9b, el_b24cc3f9f75f449698d6a63ad9b76dae, el_ee35a5aabe3845a4b1d1a2ee7633de0a, ... (+4 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: New action: -SIG_DFL : Default action for this signal. -SIG_IGN : Ignore this signal (not possible for SIGKILL or SIGSTOP ). -Handler : Adress of a signal handler f...`
- content:
```text
-SIG_DFL : Default action for this signal.

-SIG_IGN : Ignore this signal (not possible for SIGKILL or SIGSTOP ).

-Handler : Adress of a signal handler function.

sigset_t sa_mask :

Specifies a set of signals to block, while the handler is running.

Should be defined by usage of the functions sigemptyset() and sigaddset() , or sigfillset() and sigdelset() .

int sa_flags :

Flags to define the signal's behaviour:

-e. g. SA_RESTART :  Library functions like open() , read() , write()

will be resumed after execution of the signal handler.

-NULL : Library functions like open() , read() , write() ) will be terminated with errors after execution of the signal handler.

E
```

### chunk_1f3bc99528ac4a2196fe71c0dab71742
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_b9e33db9a6534309af66e4377aed8f99`
- sequence_number: `13`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `11`
- token_count: `25`
- section_path: `Usage of signal sets (I)`
- element_ids (2): `el_147fde79921d40b7860890406c9081ef, el_15706a0cfb234443a8f00e8862390474`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Usage of signal sets (I) #include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) sig_atomic_t flag = FALSE; void sigh(int); int main() { sigset...`
- content:
```text
#include <stdio.h> #include <signal.h> #define FALSE 0 #define TRUE (!FALSE) sig_atomic_t flag = FALSE; void sigh(int); int main() { sigset_t set; struct sigaction act;

DE
```

### chunk_a8a0823deebb4cd98ca752ca34ae7237
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_0ffb2a4106f7417c901752c362b022c1`
- sequence_number: `14`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `12`
- token_count: `36`
- section_path: `Usage of signal sets (II)`
- element_ids (2): `el_b5650e02c1cf42d48f663744211c309a, el_90b9a5fa5a574cf59db3e6b5fb99182a`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Usage of signal sets (II) sigemptyset(&set); sigaddset(&set, SIGINT); act.sa_flags = 0; act.sa_mask = set; act.sa_handler = &sigh; sigaction(SIGINT, &act, NULL); pr...`
- content:
```text
sigemptyset(&set); sigaddset(&set, SIGINT); act.sa_flags = 0; act.sa_mask = set; act.sa_handler = &sigh; sigaction(SIGINT, &act, NULL); printf ('Press ˆC to call the signal handler!\ n'); while (!flag) ; printf ('Programm terminates now!\ n'); return 0; }

DE
```

### chunk_401047cc49ab4f9caca90c41923b3897
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_b54d5f6ef3c4478f8db65457b206357f`
- sequence_number: `15`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `13`
- token_count: `9`
- section_path: `Usage of signal sets (III)`
- element_ids (2): `el_6f55419df4374ea58a897b2793dbb308, el_a3887e51b34a49a79141c2cde9d35635`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Usage of signal sets (III) void sigh(int signum) { flag = TRUE; } DE`
- content:
```text
void sigh(int signum) { flag = TRUE; }

DE
```

### chunk_78abfed34cb844aaaccc3837b51fe768
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_1d13d74d441a43eb9281cbb1195abb4c`
- sequence_number: `16`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `14`
- token_count: `1`
- section_path: `Signals`
- element_ids (1): `el_28ae0b30e60b4c838ef59338b1049620`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Signals DE`
- content:
```text
DE
```

### chunk_f65945faad1a4fa0994ddd4292881a41
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_2d400cc284694de7991fd7fc05e0cc01`
- sequence_number: `17`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `15`
- token_count: `46`
- section_path: `sigsetjmp() and siglongjump()`
- element_ids (2): `el_55262c91d8e94c5f9f50a7f6f2920ee2, el_2b4c7dcc87f4452caeeae5181ae6a489`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: sigsetjmp() and siglongjump() sigsetjmp(env,smask); env: adress of environment buffer smask: ≠ 0: include signal mask Return value : = 0 : first call (definition of...`
- content:
```text
sigsetjmp(env,smask); env: adress of environment buffer smask: ≠ 0: include signal mask Return value : = 0 : first call (definition of jump label) ≠ 0 : following calls (jump to label) siglongjmp(env,ret); env: adress of environment buffer ret: ≠ 0: second call of sigsetjmp()

DE
```

### chunk_96f7afccf64445aab2609255cea6f477
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_7f22433404d542c6b7ab89a82510f5ff`
- sequence_number: `18`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `16`
- token_count: `23`
- section_path: `Usage of sigsetjmp() and siglongjump() (I)`
- element_ids (2): `el_130fbd77943744058d77343bc6548203, el_d9db9fe738b3480e9fb42c81ebc428e8`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Usage of sigsetjmp() and siglongjump() (I) #include <stdio.h> #include <signal.h> #include <setjmp.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); Sigjmp_b...`
- content:
```text
#include <stdio.h>  #include <signal.h>  #include <setjmp.h> #define FALSE 0 #define TRUE (!FALSE) void sigh(int); Sigjmp_buf env; int main() { int retval; signal(SIGINT,sigh);

DE
```

### chunk_270c3ad6bd7b4db5b8614ad5b08bc9f7
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_17ce5634952e4e10945df10bf999ce01`
- sequence_number: `19`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `17`
- token_count: `86`
- section_path: `Usage of sigsetjmp() and siglongjump() (II)`
- element_ids (3): `el_4fc8e50f845a4d0aae5dc6cf99d39068, el_37a0699447a94d91b64922883bdbcebb, el_c5821d9a7da740c2a6025935ad933817`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Usage of sigsetjmp() and siglongjump() (II) if (( ret val = sigsetjmp(env,0)) == 0) {// first call printf (' sigsetjmp() has been initialised. Return value was %d.\...`
- content:
```text
if (( ret val = sigsetjmp(env,0)) == 0) {// first call printf (' sigsetjmp() has been initialised. Return value was %d.\n -> endless loop\ n', retval); while (1) ; } else // following calls printf ('Return value of sigsetjmp() was now %d.\n -> EXIT!\n ', retval); return 0; } void sigh(int signum) { siglongjmp(env,TRUE); } → Properties of signal handling: · no order defined (multiple signals), · no priorities defined, · no queues, · no data transmission, · bad programming style ( → GOTO).

DE

siglongjmp.c
```

### chunk_bce32097d71f4f2983c73009d41e85ec
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_c1f1604a0df8471eb4e9f53461ca217a`
- sequence_number: `20`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `18`
- token_count: `49`
- section_path: `Usage of pipes and FIFOs`
- element_ids (2): `el_2252e80bfa2744d08edb9c28b52491e5, el_fa6ea01252834b71bd52337d2a16528b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Usage of pipes and FIFOs int fds[2], rval; rval = pipe(fds); // create pipe write(fds [1], ...); // write access read(fds [0], ...) ; // read access int fds, rval ;...`
- content:
```text
int fds[2], rval; rval = pipe(fds); // create pipe write(fds [1], ...); // write access read(fds [0], ...) ; // read access int fds, rval ; rval = mkfifo(name,rights); // create FIFO fds = open(name,mode) // open FIFO write(fds, ...); // write access read(fds, ...); // read access

DE
```

### chunk_d4bb0f425ed24c5fb9e713a0349bee88
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_a5efa3c9b7f142198d1ebe0cb79f1e3c`
- sequence_number: `21`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `19`
- token_count: `36`
- section_path: `Message transmission with pipe() (I)`
- element_ids (2): `el_10c1e3f680344de7895b2e106da31500, el_e321423c93314c3fa4f4d8ddbd507beb`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with pipe() (I) #include <stdio.h> #include <stdlib.h> #include <sys/types.h> #include <sys/stat.h> #include <errno.h> int main(void) { pid_t n...`
- content:
```text
#include <stdio.h>  #include <stdlib.h>  #include <sys/types.h> #include <sys/stat.h>  #include <errno.h> int main(void) { pid_t npid; size_t anz; int fds[2]; char msgbuf [100]=' \ 0'; if (pipe(fds) < 0) { perror ('Pipe'); return EXIT FAILURE; }

DE
```

### chunk_bf5bfba61a7848c8b9d3979b865204d7
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_081486f83b944c3c92af129c398bae6e`
- sequence_number: `22`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `20`
- token_count: `35`
- section_path: `Message transmission with pipe() (II)`
- element_ids (2): `el_c552d347a8154cc18afd5200ef35721c, el_8bb2fea042e24860937bdfc0536abf47`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with pipe() (II) npid = fork(); if (npid) { printf ('Parent process: please type a message:\ n'); fflush (stdin); scanf ('%[ˆ \ n]', msgbuf); a...`
- content:
```text
npid = fork(); if (npid) { printf ('Parent process: please type a message:\ n'); fflush (stdin); scanf ('%[ˆ \ n]', msgbuf); anz = strlen (msgbuf)+1; write(fds[1], msgbuf, anz); printf ('Parent process: EXIT\ n'); }

DE
```

### chunk_afb6ef67c9784c50beb2cc336c11e2d8
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_9bfa3e7ee3694b3bb23e54a9f2c13802`
- sequence_number: `23`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `21`
- token_count: `61`
- section_path: `Message transmission with pipe() (III)`
- element_ids (3): `el_5f327db7c3ee4581a811f7bf21cfa566, el_10744f4a25d3428aa9de5a3b97aa9ac6, el_8d7a8e58fdf24d3c8cbab2ff93a4036e`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with pipe() (III) } else { printf ('Child process: waiting for message...\ n'); if ((anz=read(fds[0], msgbuf, sizeof(msgbuf))) != -1) { printf...`
- content:
```text
}

else { printf ('Child process: waiting for message...\ n'); if ((anz=read(fds[0], msgbuf, sizeof(msgbuf))) != -1) { printf ('Child process: I received this message: \n %s\ n', msgbuf); printf ('Child process: EXIT\ n'); } else printf ('Child process: No message for me! (error %s)!\ n', strerror(errno)); } Properties of pipes: · no names, · definition at compile time,

easy and fast.
```

### chunk_6932973863924ed5ade7f06f88acd4bc
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_a0ee34b913234d0eb1ea96119845e4f5`
- sequence_number: `24`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `21`
- token_count: `1`
- section_path: `→ Skat exercise using pipes!`
- element_ids (1): `el_fcfb10c6298d4953bee8f271e91cf820`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: → Skat exercise using pipes! DE`
- content:
```text
DE
```

### chunk_4bbafbeb54804f90bda51ab9bce1ff07
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_b8f02bdfd98940ceb69ad949bf41e63a`
- sequence_number: `25`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `22`
- token_count: `64`
- section_path: `Message transmission with FIFO (I)`
- element_ids (2): `el_7e6257563765490da5243e04012f8ede, el_6d2287a44e8d42d7b05d34878aa43fd7`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with FIFO (I) #include <stdio.h> #include <stdlib.h> #include <sys/types.h> #include <sys/stat.h> #include <fcntl.h> #include <errno.h> // Note...`
- content:
```text
#include <stdio.h>     #include <stdlib.h>  #include <sys/types.h> #include <sys/stat.h>  #include <fcntl.h>   #include <errno.h> // Note: FIFOs will not run on a Windows NTFS file system! #define TFIFO ' tfifo ' #define BUFLEN 100 #define MODE (S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH | S_IWOTH) int main(void) { pid_t npid; size_t anz; int fds; char *fifo_nam = TFIFO; char msgbuf [BUFLEN]=' \ 0';

DE
```

### chunk_2512be44e85d47d4b842716b83087781
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_60e318b446a74782a1b0f477ea58ce7f`
- sequence_number: `26`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `23`
- token_count: `60`
- section_path: `Message transmission with FIFO (II)`
- element_ids (2): `el_25c8e1e50df0486890de9394c99f691e, el_3fb5c4413e3b4ebd9954306d4d68154e`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with FIFO (II) if (mkfifo(fifo_nam, MODE) < 0) { printf ('Error creating FIFO (%s)!\ n', strerror(errno)); return EXIT FAILURE; } npid = fork()...`
- content:
```text
if (mkfifo(fifo_nam, MODE) < 0) { printf ('Error creating FIFO (%s)!\ n', strerror(errno)); return EXIT FAILURE; } npid = fork(); if (npid) { if ((fds=open(fifo_nam, O_WRONLY)) == -1) { printf ('Parent process: Could't open FIFO for writing (%s)!\ n', strerror(errno)); return EXIT FAILURE; } printf ('Parent process: Enter a message:\ n'); fflush (stdin); scanf ('%[ˆ \ n]', msgbuf); →

DE
```

### chunk_4d27a0c29ca64c3e92d7a4e3e4f05c3b
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_965602c51251403c82df41a4223b956f`
- sequence_number: `27`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `24`
- token_count: `46`
- section_path: `Message transmission with FIFO (III)`
- element_ids (2): `el_e663277d7177499a8a2a9e6f7c5e7ff4, el_b1eec0a0b68349158f531db00b7d409e`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with FIFO (III) anz = strlen(msgbuf) + 1; write(fds, msgbuf, anz); printf ('Parent process: EXIT\ n'); } else { if ((fds=open(fifo_nam, O_RDONL...`
- content:
```text
anz = strlen(msgbuf) + 1; write(fds, msgbuf, anz); printf ('Parent process: EXIT\ n'); } else { if ((fds=open(fifo_nam, O_RDONLY)) == -1) { printf ('Child process: Could't open FIFO for reading (%s)!\ n',strerror (errno)); return EXIT FAILURE; } printf ('Child process: Waiting for a message...\ n');

DE
```

### chunk_6bac34fb28e64e16b02f83a319a64c30
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_f466fdce1d02460f90ae8e645bee15c9`
- sequence_number: `28`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `25 -> 26`
- token_count: `100`
- section_path: `Message transmission with FIFO (IV)`
- element_ids (9): `el_f376ea6a778d4dadb7f5807d60241a2b, el_2489b820781748019cbf69000e7f093d, el_d7af30ee7a954373bb72a0efd91797b7, el_e9b51b5cc7044d038261491e4f4d7c47, el_3ccf4ca9746d4d1a8ee244de3c74cf96, el_776921a6216f4318b95f3caa516b5403, el_150c7111ab6e46a09e88fbf5451a4676, el_8b11cf9c96fc40e8874847fc4ab92a98, ... (+1 more)`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with FIFO (IV) if ((anz=read(fds, msgbuf, sizeof(msgbuf))) != -1) { } else } n', → Properties of FIFOs: · for multiple processes · access via n...`
- content:
```text
if ((anz=read(fds, msgbuf, sizeof(msgbuf))) != -1) { } else

}

n', → Properties of FIFOs: · for multiple processes · access via names, · definition at runtime, · still existing after program termination → Skat exercise using FIFOs!

slower.

printf ('Child process: I received this message:\n %s\ n', msgbuf); remove(fifo_nam); printf ('Child process: EXIT\ n'); printf ('Child process: No message for me (%s)!\ strerror(errno));

}

DE

mq_open() mqptr = mq_open(mq_name, oflag, rights, attrib); or mqptr = mq_open(mq_name, oflag); mqptr: Queue pointer mq_name: Name of the queue oflag: Access mode rights: Read- or write rights attrib: attributes of the queue

DE
```

### chunk_03c448cbc4624c4b9da86ca6521c5a38
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_ab4d09499ed1405dbf9c35493c1438e9`
- sequence_number: `29`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `27 -> 28`
- token_count: `63`
- section_path: `Message queues`
- element_ids (4): `el_bdb604de4568411eb5b3fbbe281f7d4b, el_8f0384a40e004a448008ebe87dac28ef, el_0a5547a19fc543e482aef17af2a82ccb, el_7e8f5cdd56d140f1814871965ffcb2cf`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message queues mq_send () mq_send(mqptr, msg, msg_len, prio); mqptr: Queue pointer msg: Pointer to date to send msg_len: number of bytes to send Prio: Priority of t...`
- content:
```text
mq_send () mq_send(mqptr, msg, msg_len, prio); mqptr: Queue pointer msg: Pointer to date to send msg_len: number of bytes to send Prio: Priority of the message

DE

mq_receive () size = mq_receive(mqptr, msg, msg_len, prio_ptr); size: size of the message in bytes mqptr: Queue pointer msg: Pointer to receive buffer msg_len: Size of receive buffer in bytes prio_ptr: Pointer to priority variable

DE
```

### chunk_33ee511bf5b040aca63f13416475d751
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_02c199472b404f388fdf746fffccbb94`
- sequence_number: `30`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `29`
- token_count: `64`
- section_path: `Message transmission with queues (I)`
- element_ids (2): `el_f18deee587954d6a8e13339b4ba9f905, el_c0ad942681d5424b999874db7cdaab73`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with queues (I) #include <stdio.h> #include <stdlib.h> #include <string.h> #include <unistd.h> #include <sys/stat.h> #include <mqueue.h> #inclu...`
- content:
```text
#include <stdio.h>  #include <stdlib.h>  #include <string.h>  #include <unistd.h> #include <sys/stat.h>  #include <mqueue.h>  #include <errno.h> // Note (20200330): message queues are not implemented for //                  Ubuntu 18.04 in a Windows 10 subsystem! #define ZMAX 80 #define PRIO 0 #define MODE (S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH |S_IWOTH) int main(void) { char msgbuf[ZMAX], tmq_name []='/ tmq '; unsigned int prio; pid_t npid; mqd_t tmq; size_t anz; struct mq_attr mqattr; →

DE
```

### chunk_54f93a59befa4840a255152538c445dd
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_b95badf2d9b64c25afac003a2985f6a0`
- sequence_number: `31`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `30`
- token_count: `44`
- section_path: `Message transmission with queues (II)`
- element_ids (2): `el_67f3200b318444a6b6515059cd3c6589, el_a060e9d4b8d9465a9d2599df8dd7b68b`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with queues (II) npid = fork(); if (npid) { sleep(1); if ((tmq=mq open(tmq_name, O WRONLY)) == -1) { printf ('Parent process: Can't open %s\ n'...`
- content:
```text
npid = fork(); if (npid) { sleep(1); if ((tmq=mq open(tmq_name, O WRONLY)) == -1) { printf ('Parent process: Can't open %s\ n', tmq_name); return EXIT FAILURE; } printf ('Parent process: Please type a message:\ n'); fflush (stdin) ; scanf ('%[ˆ \ n]', msgbuf);

DE
```

### chunk_7207c69c23994289bef66b99f146a4ce
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_b0251e72de794859a82c946c05c49ff7`
- sequence_number: `32`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `31`
- token_count: `44`
- section_path: `Message transmission with queues (III)`
- element_ids (2): `el_a5018ae80da6418c9a6a358580cfd8dc, el_782c572aa882456db634a18e2df3f888`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with queues (III) if (mq_send(tmq, msgbuf, sizeof(msgbuf),PRIO) == -1) { printf ('Parent process: %s is not accessible\ n', tmq_name); return E...`
- content:
```text
if (mq_send(tmq, msgbuf, sizeof(msgbuf),PRIO) == -1) { printf ('Parent process: %s is not accessible\ n', tmq_name); return EXIT FAILURE; } if (mq_close(tmq) == -1) { printf ('Parent process: Can't close %s\ n',tmq_name ); return EXIT FAILURE; } printf ('Parent process: EXIT\ n'); }

DE
```

### chunk_a17262fffc674adb9aa818dc5f5239da
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_508e7d87d35b42b2ac06a511d7931193`
- sequence_number: `33`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `32`
- token_count: `48`
- section_path: `Message transmission with queues (IV)`
- element_ids (2): `el_8e1b0a9e293b42ebb77ec9564a78b658, el_da38f84ee2f547e8b0d1ac6c651f0d30`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with queues (IV) else { mqattr.mq maxmsg = 10; mqattr.mq msgsize = ZMAX; mqattr.mq flags = 0; if ((tmq=mq open(tmq_name, O CREAT|O RDWR, MODE,...`
- content:
```text
else { mqattr.mq maxmsg = 10; mqattr.mq msgsize = ZMAX; mqattr.mq flags = 0; if ((tmq=mq open(tmq_name, O CREAT|O RDWR, MODE, &mqattr)) == -1) { printf ('Child process: Can't create Message Queue %s\ n', tmq_name); return EXIT FAILURE; } printf ('Child process: Waiting for a message...\ n');

DE
```

### chunk_5fcb47e08fd04f979e60282a542879da
- document id: `doc_117323b53fa54c898ec1a932956d103a`
- section id: `sec_f002b762055748c9b3602bd00d104487`
- sequence_number: `34`
- chunk_index/chunk_total: `1/1`
- chunk type: `general`
- page_start/page_end: `33`
- token_count: `91`
- section_path: `Message transmission with queues (V)`
- element_ids (3): `el_032146948ea74eb2bb8035d79b7deccd, el_c12ffc0b27b44b6c9d1c44dcb4218b5c, el_d81cca62012645cc95f9db87696b31b5`
- table_ids (0): ``
- picture_ids (0): ``
- embedding_text preview: `Document title: 10 OS-BS 2020 Interprocess communication E Section path: Message transmission with queues (V) } if((anz=mq_receive(tmq,msgbuf,sizeof(msgbuf),&prio))>0){ printf ('Child process: I received this message:\n %s\ n', msgbuf);...`
- content:
```text
}

if((anz=mq_receive(tmq,msgbuf,sizeof(msgbuf),&prio))>0){ printf ('Child process: I received this message:\n %s\ n', msgbuf); printf ('Child process: EXIT\ n'); } else printf ('Child process: No message for me!\ n'); if (mq unlink(tmq_name) != 0) { printf ('Child process: Can't remove Message Queue %s (%s)\ n', tmq_name, strerror(errno)); return EXIT FAILURE; } } return EXIT SUCCESS; → queues.c Properties of message queues: · available in all OS, · priorities · well defined order of delivery, · handling is similar to files but done by drivers (not file system). → Skat exercise using queues!

DE
```

## Warnings

### Validation
- sections with parent_section_id: `0`
- root sections: `42`
- elements without section_id: `0`
- chunks without section_path: `0`
- chunks spanning multiple elements: `30`
- chunks spanning multiple pages: `3`
- normal text elements with self-derived section_title: `0`

### Warnings
- No table assets were detected.
- All sections are root sections.
