<template>
    <div class="d-flex flex-column align-center justify-top mt-5 pa-5">
        <h1 class="ma-0">{{ level }}. Feladat</h1>
        <div v-if="teamInfo" class="d-flex flex-column align-center justify-top mt-2 ">
            <p class="ma-0">Csapatnév: {{ teamInfo.teamName }}</p>
            <p class="ma-0">Kiválasztott nehézség: {{ difficultyDescriptions[teamInfo.difficulty] }}</p>
        </div>
        <v-progress-circular v-if="isLoadingTeamInfo" indeterminate />
        <div v-if="isLoadingProblem" class="d-flex align-center justify-center fill-height">
            <v-progress-circular
            color="grey-lighten-4"
            indeterminate
            ></v-progress-circular>
        </div>
        <v-img
            v-else
            class="ma-5"
            width="500"
            rounded="xl"
            :src="problemSource"
            fit
        />
        <h3 class="ma-0 mt-5">Megoldás:</h3>
        <div class="d-flex justify-center align-center flex-wrap ga-5">
            <v-otp-input
                v-model="inputText"
                rounded="pill"
                length="4"
                autofocus
                :disabled="disableInput"
            />
            <v-btn
                size="large"
                rounded="pill"
                prepend-icon="mdi-arrow-right-bottom"
                :disabled="inputText.length !== 4 || disableInput"
                :loading="isCheckingSolution"
                @click="sendAnswer()"
            >
                Beküldés
            </v-btn>
            <v-dialog v-model="isAnswerCheckPopupOpen" max-width="800px">
                <v-card rounded="xl" :color="answerResponse === AnswerResponse.Wrong ? 'red' : 'success'">
                    <v-card-text class="text-background">
                        {{ answerCheckPopupText[answerResponse] }}
                    </v-card-text>
                    <v-card-actions class="justify-center">
                        <v-btn
                            rounded="pill"
                            variant="tonal"
                            color="background"
                            @click="cardButtonClicked()"
                        >
                            {{ answerCheckButtonLabel[answerResponse] }}
                        </v-btn>
                        <v-btn
                            v-if="level >= 6 && answerResponse === AnswerResponse.Wrong"
                            rounded="pill"
                            variant="tonal"
                            color="background"
                            @click="giveUp()"
                        >
                            Feladom
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
            <v-snackbar v-model="didEncounterError" color="red">
                {{ errorMessage }}
            </v-snackbar>
        </div>
    </div>
</template>

<script setup>
    const props = defineProps({
        level: Number
    })

    import { onMounted, ref } from 'vue';
    import { AnswerResponse, difficultyDescriptions, getApiBasePath } from "@/common/common";

    let answerCheckPopupText = {
        [AnswerResponse.Wrong]: "A megoldásod sajnos nem helyes",
        [AnswerResponse.Correct]: "Helyes megoldás!",
        [AnswerResponse.Finished]: "Helyes megoldás! Ezzel megoldottátok az összes feladatot!"
    };

    let answerCheckButtonLabel = {
        [AnswerResponse.Wrong]: "Újrapróbálkozom",
        [AnswerResponse.Correct]: "Folytatás",
        [AnswerResponse.Finished]: "Tovább"
    };

    const apiBasePath = getApiBasePath();
    const teamToken = localStorage.getItem("teamToken");

    if (teamToken === null) {
        window.location.href = "/regisztracio/";
    }

    const teamInfo = ref(null);
    const disableInput = ref(false);
    const inputText = ref("");
    const isCheckingSolution = ref(false);
    const isLoadingProblem = ref(false);
    const isLoadingTeamInfo = ref(false);
    const isAnswerCheckPopupOpen = ref(false);
    const answerResponse = ref(AnswerResponse.Wrong);
    const problemSource = ref("");
    const didEncounterError = ref(false);
    const errorMessage = ref("");

    onMounted(async () => {
        await getTeamInfo();
        await getProblem();
    });

    function couldntGetProblem() {
        errorMessage.value = "Hiba történt a feladat betöltése során, frissítsd újra az oldalt";
        didEncounterError.value = true;
        isLoadingProblem.value = false;
        problemSource.value = "";
    }

    function couldntSendAnswer() {
        errorMessage.value = "Hiba történt a beküldés során, próbáld újra";
        didEncounterError.value = true;
    }

    function couldntGetTeamInfo() {
        errorMessage.value = "Hiba történt a csapat lekérdezése közben, frissítsd újra az oldalt";
        didEncounterError.value = true;
        disableInput.value = true;
        isLoadingTeamInfo.value = false;
    }

    async function getTeamInfo() {
        isLoadingTeamInfo.value = true;
        await fetch(new URL("/info", apiBasePath), {
            method: "GET",
            headers: {
                "Authorization": teamToken
            },
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntGetTeamInfo();
            }
            else {
                const result = await response.json();
                isLoadingProblem.value = false;
                if (props.level > result.currentLevel) {
                    window.location.href = `/feladat/${result.currentLevel}`;
                }
                teamInfo.value = result;
                console.log(result);
                isLoadingTeamInfo.value = false;
            }
        },
        (error) => {
            couldntGetTeamInfo();
        });
    }

    async function getProblem() {
        problemSource.value = "";
        isLoadingProblem.value = true;
        await fetch(new URL("/problem", apiBasePath), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": teamToken
            },
            body: JSON.stringify({
                level: props.level
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntGetProblem();
            }
            else {
                const blob = await response.blob();
                problemSource.value = URL.createObjectURL(blob);
                isLoadingProblem.value = false;
            }
        },
        (error) => {
            couldntGetProblem();
        });
    }

    function sendAnswer() {
        isCheckingSolution.value = true;
        fetch(new URL("/check", apiBasePath), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": teamToken
            },
            body: JSON.stringify({
                level: props.level,
                answer: Number(inputText.value)
            }),
            signal: AbortSignal.timeout(5000)
        }).then(
            async (response) => {
                if (!response.ok) {
                    isCheckingSolution.value = false;
                    couldntSendAnswer();
                    return;
                }
                const result = await response.json();
                isCheckingSolution.value = false;
                answerResponse.value = result.result;
                console.log("Answer response:", answerResponse.value);
                isAnswerCheckPopupOpen.value = true;
            },
            (error) => {
                isCheckingSolution.value = false;
                couldntSendAnswer();
            }
        );
    }

    function cardButtonClicked() {
        if (answerResponse.value === AnswerResponse.Correct) {
            window.location.href = `/feladat/${props.level + 1}`;
        }
        else if (answerResponse.value === AnswerResponse.Finished) {
            window.location.href = "/eredmenyek";
        }
        else {
            isAnswerCheckPopupOpen.value = !isAnswerCheckPopupOpen.value;
        }
    }

    function giveUp() {
        window.location.href = "/eredmenyek";
    }
</script>