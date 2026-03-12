<template>
    <div class="d-flex flex-column align-center justify-top">
        <h1>Regisztráció</h1>
        <v-container>
            <v-row justify="center">
                <v-col cols="11" md="10" lg="6">
                    <v-form ref="form" @submit.prevent="submit">
                        <v-text-field
                            v-model="teamName"
                            label="Csapatnév"
                            :rules="nameRules"
                            :error-messages="teamNameAsyncError"
                            :disabled="isRegistrationLoading"
                            required
                        />
                        <v-select
                            v-model="difficulty"
                            label="Nehézség"
                            item-title="label"
                            item-value="value"
                            :items="difficultyItems"
                            :rules="difficultyRules"
                            :disabled="isRegistrationLoading"
                        />
                        <v-btn
                            class="mt-5"
                            size="large"
                            text="Regisztráció"
                            type="submit"
                            rounded="pill"
                            :loading="isRegistrationLoading"
                            block
                        />
                    </v-form>
                </v-col>
            </v-row>
        </v-container>
        <v-snackbar v-model="didEncounterError" color="red">
            {{ errorMessage }}
        </v-snackbar>
        <v-snackbar v-model="didSuccessfullyRegister" color="green">
            Sikeres regisztráció
        </v-snackbar>
    </div>
</template>

<script setup>
    import { ref, watch } from 'vue';
    import { Difficulty } from "@/constants/common.ts";

    const nameRules = [
        v => !!v || "A csapatnevet kötelező kitölteni",
        v => v.trim().length > 0 || "A csapatnév nem lehet csak szóköz",
        v => v === v.trim() || "A csapatnév nem kezdődhet vagy végződhet szóközzel",
        v => v.length <= 25 || "Maximum 25 karakter"
    ];

    const difficultyRules = [
        v => v !== null || "Kötelező kiválasztani nehézséget"
    ]

    const difficultyItems = [
        {label: "Könnyebb (6 feladat)", value: Difficulty.Easy},
        {label: "Nehezebb (8 feladat)", value: Difficulty.Hard}
    ]

    const apiBasePath = `${window.location.protocol}//${window.location.hostname}:8000/`;

    const form = ref(null);
    const teamName = ref("");
    const difficulty = ref(null);
    const teamNameAsyncError = ref("");
    const isRegistrationLoading = ref(false);
    const didEncounterError = ref(false);
    const errorMessage = ref("");
    const didSuccessfullyRegister = ref(false);

    watch(teamName, () => {
        teamNameAsyncError.value = ""
    })

    async function checkTeamNameAvailability() {
        return await fetch(new URL("/available", apiBasePath), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                teamName: teamName.value
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                errorMessage.value = "Hiba történt a csapatnév ellenőrzése során, próbáld meg újra"
                didEncounterError.value = true;
                return false;
            }
            else {
                const result = await response.json();
                if (result.available) {
                    teamNameAsyncError.value = "";
                    return true;
                }
                else {
                    teamNameAsyncError.value = "Ez a csapatnév már foglalt";
                    isRegistrationLoading.value = false;
                    return false;
                }
            }
        },
        (error) => {
            errorMessage.value = "Hiba történt a csapatnév ellenőrzése során, próbáld meg újra"
            didEncounterError.value = true;
            return false;
        });
    };

    async function sendRegistration() {
        return await fetch(new URL("/register", apiBasePath), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                teamName: teamName.value,
                difficulty: difficulty.value
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                errorMessage.value = "Hiba történt a csapat regisztrálása során, próbáld meg újra"
                didEncounterError.value = true;
                isRegistrationLoading.value = false;
            }
            else {
                const result = await response.json();
                localStorage.setItem("teamToken", result.token);
                didSuccessfullyRegister.value = true;
                isRegistrationLoading.value = false;
                window.location.href = "/feladat/1";
            }
        },
        (error) => {
            errorMessage.value = "Hiba történt a csapat regisztrálása során, próbáld meg újra"
            didEncounterError.value = true;
            isRegistrationLoading.value = false;
        });
    }

    async function submit() {
        teamNameAsyncError.value = "";
        const { valid } = await form.value.validate();
        if (!valid) {
            return;
        }
        isRegistrationLoading.value = true;

        const isTeamNameAvailable = await checkTeamNameAvailability();
        if (!isTeamNameAvailable) {
            isRegistrationLoading.value = false;
            return;
        }


        await sendRegistration();
    }
</script>