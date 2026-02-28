<template>
    <div class="d-flex flex-column align-center justify-top">
        <h1>#{{ level }} Feladat</h1>
        <div class="d-flex justify-center align-center flex-wrap ga-5">
            <v-otp-input v-model="inputText" rounded="pill" length="4" autofocus></v-otp-input>
            <v-btn
            size="large"
            rounded="pill"
            prepend-icon="mdi-arrow-right-bottom"
            :disabled="inputText.length !== 4"
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
                        <p class="text-background">
                            Tipp a következő feladathoz:
                        </p>
                        <div v-if="isLoadingTip" class="d-flex align-center justify-center fill-height">
                            <v-progress-circular
                            color="grey-lighten-4"
                            indeterminate
                            ></v-progress-circular>
                        </div>
                        <v-img
                        v-else
                        :src="tipSource"
                        >
                        </v-img>
                    </div>
                    <v-card-actions class="justify-center">
                        <v-btn rounded="pill" variant="tonal" color="background" @click="isAnswerCheckPopupOpen = !isAnswerCheckPopupOpen">
                            {{ wasAnswerCorrect ? "Folytatás" : "Újrapróbálkozom"}}
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
            <v-snackbar v-model="couldntSendAnswer" color="red">
                Hiba történt a beküldés során, próbáld újra
            </v-snackbar>
            <v-snackbar v-model="couldntGetTip" color="red">
                Hiba történt a tipp betöltése során, próbálja újra
            </v-snackbar>
        </div>
    </div>
</template>

<script setup>
    const props = defineProps({
        level: Number
    })

    import { ref } from 'vue';

    const apiBasePath = `http://${window.location.hostname}:8000/`;

    const inputText = ref("");
    const isCheckingSolution = ref(false);
    const isLoadingTip = ref(false);
    const couldntSendAnswer = ref(false);
    const couldntGetTip = ref(false);
    const isAnswerCheckPopupOpen = ref(false);
    const wasAnswerCorrect = ref(false);
    const tipSource = ref("");

    function getTip() {
        tipSource.value = "";
        isLoadingTip.value = true;
        fetch(new URL("/tip/", apiBasePath), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                level: props.level,
                answer: Number(inputText.value)
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                tipSource.value = "";
                couldntGetTip.value = true;
                isLoadingTip.value = false;
            }
            else {
                const blob = await response.blob();
                tipSource.value = URL.createObjectURL(blob);
                isLoadingTip.value = false;
            }
        },
        (error) => {
            tipSource.value = "";
            couldntGetTip.value = true;
            isLoadingTip.value = false;
        });
    }

    function sendAnswer() {
        isCheckingSolution.value = true;
        fetch(new URL("/check/", apiBasePath), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
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
                    couldntSendAnswer.value = true;
                }
                const result = await response.json();
                isCheckingSolution.value = false;
                console.log(result);
                if (result.correct) {
                    wasAnswerCorrect.value = true;
                    getTip();
                }
                else {
                    wasAnswerCorrect.value = false;
                }
                isAnswerCheckPopupOpen.value = true;
            },
            (error) => {
                isCheckingSolution.value = false;
                couldntSendAnswer.value = true;
            }
        );
    }
</script>

<style>
</style>