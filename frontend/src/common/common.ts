export enum Difficulty {
    Easy = 0,
    Hard = 1
};

export enum AnswerResponse {
    Wrong = 0,
    Correct = 1,
    Finished = 2
};

export let difficultyDescriptions: Record<Difficulty, string> = {
    [Difficulty.Easy]: "Könnyebb",
    [Difficulty.Hard]: "Nehezebb"
};

export let difficultyNumLevels: Record<Difficulty, Number> = {
    [Difficulty.Easy]: 6,
    [Difficulty.Hard]: 8
};

type Rule<T = string> = (value: T) => true | string;

export const nameRules: Rule<string>[] = [
    v => !!v || "A csapatnevet kötelező kitölteni",
    v => v.trim().length > 0 || "A csapatnév nem lehet csak szóköz",
    v => v === v.trim() || "A csapatnév nem kezdődhet vagy végződhet szóközzel",
    v => v.length <= 25 || "Maximum 25 karakter"
];

export const difficultyRules: Rule<string>[] = [
    v => v !== null || "Kötelező kiválasztani nehézséget"
]

export const difficultyItems = [
    {label: "Könnyebb (6 feladat)", value: Difficulty.Easy},
    {label: "Nehezebb (8 feladat)", value: Difficulty.Hard}
]

export function getApiBasePath() {
    return `${window.location.protocol}//${window.location.hostname}:3501/`;
}

export async function checkTeamNameAvailability(teamName: string) {
    return new Promise(async (resolve, reject) => {
        await fetch(new URL("/available", getApiBasePath()), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                teamName: teamName
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                reject(response.statusText);
            }
            else {
                const result = await response.json();
                if (result.available) {
                    resolve(true);
                }
                else {
                    resolve(false);
                }
            }
        },
        (error) => {
            reject(error);
        });
    })
        
};