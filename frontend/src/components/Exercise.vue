<template>
    <div class="d-flex flex-column align-center justify-top mt-5 pa-5">
        <h1 class="ma-0">{{ level }}. Feladat</h1>
        <div v-if="teamInfo" class="d-flex flex-column align-center justify-top mt-2 ">
            <p class="ma-0">Csapatnév: {{ teamInfo.teamName }}</p>
            <p class="ma-0">Kiválasztott nehézség: {{ teamInfo.difficulty === Difficulty.Easy ? "Könnyebb" : "Nehezebb" }}</p>
        </div>
        <div v-if="isLoadingProblem" class="d-flex align-center justify-center fill-height">
            <v-progress-circular
            color="grey-lighten-4"
            indeterminate
            ></v-progress-circular>
        </div>
        <v-img
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
                <v-card rounded="xl" :color="wasAnswerCorrect ? 'success' : 'red'">
                    <v-card-text class="text-background">
                        {{ wasAnswerCorrect ? "Helyes megoldás!" : "A megoldásod sajnos nem helyes" }}
                    </v-card-text>
                    <div v-if="wasAnswerCorrect" class="ml-5 mr-5 mb-6">
                        <Teleport to="body">
                            <div class="position-absolute confetti-wrapper">
                                <ConfettiExplosion
                                    v-if="doShowConfetti"
                                    :force="0.8"
                                    :stageWidth="confettiStageWidth"
                                />
                            </div>
                        </Teleport>
                    </div>
                    <v-card-actions class="justify-center">
                        <v-btn
                            rounded="pill"
                            variant="tonal"
                            color="background"
                            @click="cardButtonClicked()"
                        >
                            {{ wasAnswerCorrect ? "Folytatás" : "Újrapróbálkozom"}}
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

    import { onMounted, ref, watch } from 'vue';
    import ConfettiExplosion from "vue-confetti-explosion";

    const Difficulty = {
        Easy: 0,
        Hard: 1
    }

    const apiBasePath = `${window.location.protocol}//${window.location.hostname}:8000/`;
    const teamToken = localStorage.getItem("teamToken");

    if (teamToken === null) {
        window.location.href = "/regisztracio/";
    }

    const teamInfo = ref(null);
    const disableInput = ref(false);
    const inputText = ref("");
    const isCheckingSolution = ref(false);
    const isLoadingProblem = ref(false);
    const isAnswerCheckPopupOpen = ref(false);
    const wasAnswerCorrect = ref(false);
    const problemSource = ref("");
    const doShowConfetti = ref(false);
    const confettiStageWidth = ref(getConfettiStageWidth());
    const didEncounterError = ref(false);
    const errorMessage = ref("");

    onMounted(async () => {
        await getTeamInfo();
        await getProblem();
    });
    
    watch(isAnswerCheckPopupOpen, (val) => {
        document.documentElement.classList.toggle('no-scroll', val);
        document.body.classList.toggle('no-scroll', val);
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
    }

    function getConfettiStageWidth() {
        const aspectRatio = window.innerWidth / window.innerHeight;
        const scale = 1 / Math.pow(aspectRatio, 0.4) + 0.2;
        return window.innerWidth * scale;
    }

    async function getTeamInfo() {
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
            }
        },
        (error) => {
            couldntGetTeamInfo();
        });
    }

    async function getProblem() {
        doShowConfetti.value = false;
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
                confettiStageWidth.value = getConfettiStageWidth();
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
                }
                const result = await response.json();
                isCheckingSolution.value = false;
                if (result.correct) {
                    wasAnswerCorrect.value = true;
                }
                else {
                    wasAnswerCorrect.value = false;
                }
                isAnswerCheckPopupOpen.value = true;
            },
            (error) => {
                isCheckingSolution.value = false;
                couldntSendAnswer();
            }
        );
    }

    function cardButtonClicked() {
        if (wasAnswerCorrect.value) {
            window.location.href = `/feladat/${props.level + 1}`;
        }
        else {
            isAnswerCheckPopupOpen.value = !isAnswerCheckPopupOpen.value;
        }
    }
</script>

<style>
.no-scroll {
    overflow: hidden !important;
    height: 100%;
}

.confetti-wrapper {
    top: 50%;
    left: 50%;
    z-index: 9999;
    transform: translate(-50%, -50%);
    pointer-events: none;
}
</style>