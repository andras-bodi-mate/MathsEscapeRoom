export enum Difficulty {
  Easy = 0,
  Hard = 1
}


export enum AnswerResponse {
  Wrong = 0,
  Correct = 1,
  Finished = 2
}

export let difficultyDescriptions: Record<Difficulty, string> = {
  [Difficulty.Easy]: "Könnyebb",
  [Difficulty.Hard]: "Nehezebb"
};

export let difficultyNumLevels: Record<Difficulty, Number> = {
  [Difficulty.Easy]: 6,
  [Difficulty.Hard]: 8
}