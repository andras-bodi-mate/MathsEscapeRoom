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
                    <v-card-actions class="justify-center">
                        <v-btn rounded="pill" variant="tonal" color="background" @click="isAnswerCheckPopupOpen = !isAnswerCheckPopupOpen">
                            {{ wasAnswerCorrect ? "Folytatás" : "Újrapróbálkozom"}}
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
            <v-snackbar v-model="isSnackbarOpen" color="red">
                Hiba történt a beküldés során, próbáld újra
            </v-snackbar>
        </div>
    </div>
</template>

<script setup>
    const props = defineProps({
        level: Number
    })

    import { ref } from 'vue';
    const inputText = ref("");
    const isCheckingSolution = ref(false);
    const isSnackbarOpen = ref(false);
    const isAnswerCheckPopupOpen = ref(false);
    const wasAnswerCorrect = ref(false);

    function sendAnswer() {
        isCheckingSolution.value = true;
        fetch(`http://${window.location.hostname}:8000/check/`, {
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
                    isSnackbarOpen.value = true;
                }
                const result = await response.json();
                isCheckingSolution.value = false;
                console.log(result);
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
                isSnackbarOpen.value = true;
            }
        );
    }
</script>

<style>
</style>