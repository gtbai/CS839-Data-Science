---
layout: default
title: Project Stage 3
nav_order: 4
---

# Project Stage 3

## Matching Fodors and Zagats

+ User ID: `bugwriter`
+ Project ID: `trial`
<!-- + [Screen Shot](https://github.com/gtbai/CS839-Data-Science/blob/master/stage3/trial/screen_shot.png) -->
+ Screenshot:
  ![Screenshot](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/trial/screen_shot.png)

## Blocking Results

+ User ID: `bugwriter`
+ Project ID: `movies`
+ Screenshot: ![Screenshot](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/blocking/screen_shot.png)

## Matching Results

+ User ID: `bugwriter`
+ Project ID: `movies`
+ Screenshot: ![Screenshot](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/matching/screen_shot.png)

## Estimating Accuracy

### Links
+ [Prediction list](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/estimating/falcon_cm_matching_al_ds)
+ [Candidate set](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/estimating/falcon_apply_rules_ds)
+ [Table A](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/estimating/imdb)
+ [Table B](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/estimating/tmdb)

### Analysis 
+ Size of the candidate set C: 3179
+ [PDF file](https://github.com/gtbai/CS839-Data-Science/blob/master/stage3/estimating/Iterations.pdf)
+ Blocking code: Because the program terminates at the first iteration, we don't need any blocking rules/code to reduce the size of the candidate set C.
+ [Final reduced set of candidate tuple pairs](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/estimating/falcon_apply_rules_ds): It is still the candidate set C.
+ [400 tuples sampled and manually labeled](https://raw.githubusercontent.com/gtbai/CS839-Data-Science/master/stage3/estimating/labeled_pairs.csv)
+ Jupyter notebook output: ((0.989417801886328, 1.003202124312934), (1.0, 1.0))
+ Recall = [0.989 - 1.003]
+ Precision = [1.0 - 1.0]



