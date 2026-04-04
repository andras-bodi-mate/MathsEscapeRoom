<template>
    <div class="d-flex flex-column align-center text-center justify-top mt-5 pa-5">
        <h1>Szabadulószoba Kezelőfelület</h1>
        <div class="d-flex ga-2 align-center">
            <p class="ma-3">Játék státusza: </p>
            <v-chip v-if="gameState" :color="statusColors[gameState.status]">{{ statusNames[gameState.status] }}</v-chip>
            <p v-else-if="!isGameStateLoading" class="ma-0">—</p>
            <v-progress-circular v-if="isGameStateLoading" size="small" indeterminate></v-progress-circular>
        </div>
        <div v-if="gameState" class="d-flex ga-3">
            <v-btn
                v-if="gameState.status !== GameStatus.Started"
                text="Indítás"
                prepend-icon="mdi-play"
                color="green"
                variant="tonal"
                :loading="isGameStartLoading"
                :readonly="isStatusChangeLoading"
                @click="startGame"
            ></v-btn>
            <v-btn
                v-if="gameState.status !== GameStatus.Stopped"
                text="Leállítás"
                prepend-icon="mdi-stop"
                :loading="isGameStopLoading"
                :readonly="isStatusChangeLoading"
                @click="isStoppingGame = true"
            ></v-btn>
        </div>
        <v-data-table class="table mt-5 rounded-xl overflow-hidden pa-5 ma-5 text-left" :headers="teamHeaders" :items="teams" :loading="isReloadingTeams" :hide-default-footer="teams.length <= 10">
            <template #top>
                <v-card-title class="d-flex justify-center">Csapatok</v-card-title>
                <v-card-subtitle v-if="!isReloadingTeams" class="d-flex justify-center">Csapatok száma: {{ isReloadingTeams ? "" : teams.length }}</v-card-subtitle>
            </template>
            <template v-slot:item.actions="{ item }">
                <div class="d-flex ga-5 justify-end">
                    <v-tooltip location="top">
                        <template v-slot:activator="{ props }">
                            <v-icon v-bind="props" color="extra-emphasis" icon="mdi-pencil" @click="openTeamModificationDialog(item)"></v-icon>
                        </template>
                        Módosítás
                    </v-tooltip>

                    <v-tooltip location="top">
                        <template v-slot:activator="{ props }">
                            <v-icon v-bind="props" color="high-emphasis" icon="mdi-delete" @click="confirmTeamDeletion(item)"></v-icon>
                        </template>
                        Törlés
                    </v-tooltip>
                </div>
            </template>
        </v-data-table>
        <v-data-table class="table mt-5 rounded-xl overflow-hidden pa-5 ma-5 text-left"  :headers="exerciseHeaders" :items="exercises" :loading="isReloadingExercises" :hide-default-footer="exercises.length <= 10">
            <template #top>
                <v-card-title class="d-flex justify-center">Feladatok</v-card-title>
                <v-card-subtitle v-if="!isReloadingExercises" class="d-flex justify-center">Feladatok száma: {{ isReloadingExercises ? "" : exercises.length }}</v-card-subtitle>
            </template>
            <template v-slot:item.actions="{ item }">
                <div class="d-flex ga-5 justify-end">
                    <v-tooltip location="top">
                        <template v-slot:activator="{ props }">
                            <v-icon v-bind="props" color="extra-emphasis" icon="mdi-pencil" @click="openExerciseModificationDialog(item)"></v-icon>
                        </template>
                        Módosítás
                    </v-tooltip>

                    <v-tooltip location="top">
                        <template v-slot:activator="{ props }">
                            <v-icon v-bind="props" color="high-emphasis" icon="mdi-delete" @click="confirmExerciseDeletion(item)"></v-icon>
                        </template>
                        Törlés
                    </v-tooltip>
                </div>
            </template>
        </v-data-table>
        <v-btn prepend-icon="mdi-reload" :loading="isReloadingTeams" @click="reloadEverything">Frissítés</v-btn>
        <v-snackbar v-model="didEncounterError" color="red">
            {{ errorMessage }}
        </v-snackbar>
    </div>
    <v-dialog v-model="isDeletingTeam" max-width="500">
        <v-card class="rounded-xl" title="Megerősítés">
            <v-card-text>
                <p>
                    Biztosan törölni akarod a
                    <strong>
                        {{ teamBeingDeleted.name }}
                    </strong>
                    csapatot?
                </p>
            </v-card-text>
            <v-card-actions class="justify-space-between ml-5 mr-5 mb-2">
                <v-btn text="Vissza" rounded="pill" @click="isDeletingTeam = false"></v-btn>
                <v-btn text="Törlés" color="red" variant="tonal" rounded="pill" @click="deleteTeam(teamBeingDeleted)"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isModifyingTeam" max-width="800">
        <v-card class="rounded-xl" title="Módosítás" :loading="isGameStopLoading">
            <v-card-text>
                <v-form :ref="(el) => teamModificationForm = el" >
                    <v-text-field
                        v-model="modifiedTeam.name"
                        label="Új csapatnév"
                        :rules="nameRules"
                        :error-messages="teamNameAsyncError"
                        :disabled="isTeamModificationLoading"
                        required
                    />
                    <v-select
                        v-model="modifiedTeam.difficulty"
                        label="Új nehézség"
                        item-title="label"
                        item-value="value"
                        :items="difficultyItems"
                        :rules="difficultyRules"
                        :disabled="isTeamModificationLoading"
                        @update:modelValue="modifiedTeam.currentLevel = Math.min(
                            difficultyNumLevels[modifiedTeam.difficulty], modifiedTeam.currentLevel
                        )"
                    />
                    <div class="d-flex ga-5">
                        <v-number-input
                            v-model="modifiedTeam.currentLevel"
                            label="Új aktuális feladat"
                            :min="1"
                            :max="difficultyNumLevels[modifiedTeam.difficulty]"
                            :disabled="isFinished || isTeamModificationLoading"
                        >
                        </v-number-input>
                        <v-checkbox
                            v-model="isFinished"
                            label="Végzett"
                            :disabled="isTeamModificationLoading"
                        >
                        </v-checkbox>
                    </div>
                </v-form>
            </v-card-text>
            <v-card-actions class="justify-space-between ml-5 mr-5 mb-2">
                <v-btn text="Vissza" rounded="pill" @click="isModifyingTeam = false"></v-btn>
                <v-btn text="Módosítás" type="submit" variant="tonal" rounded="pill" :loading="isTeamModificationLoading" @click="onTeamModificationSubmission"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isDeletingExercise" max-width="500">
        <v-card class="rounded-xl" title="Megerősítés">
            <v-card-text>
                <p>
                    Biztosan törölni akarod a
                    <strong>
                        {{ `${exerciseBeingDeleted.level}. (${exerciseBeingDeleted.title})` }}
                    </strong>
                    feladatot?
                </p>
            </v-card-text>
            <v-card-actions class="justify-space-between ml-5 mr-5 mb-2">
                <v-btn text="Vissza" rounded="pill" @click="isDeletingExercise = false"></v-btn>
                <v-btn text="Törlés" color="red" variant="tonal" rounded="pill" @click="deleteExercise(exerciseBeingDeleted)"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isModifyingExercise" max-width="800">
        <v-card class="rounded-xl" title="Módosítás" :loading="isGameStopLoading">
            <v-card-text>
                <v-form :ref="(el) => exerciseModificationForm = el" >
                    <v-number-input
                        v-model="modifiedExercise.level"
                        label="Új sorszám"
                        :min="1"
                        :disabled="isExerciseModificationLoading"
                    >
                    </v-number-input>
                    <v-text-field
                        v-model="modifiedExercise.title"
                        label="Új cím"
                        :rules="nameRules"
                        :error-messages="exerciseTitleAsyncError"
                        :disabled="isExerciseModificationLoading"
                        required
                    />
                    <v-number-input
                        v-model="modifiedExercise.solution"
                        label="Új megoldás"
                        :min="1000"
                        :max="9999"
                        :disabled="isExerciseModificationLoading"
                    >
                    </v-number-input>
                </v-form>
            </v-card-text>
            <v-card-actions class="justify-space-between ml-5 mr-5 mb-2">
                <v-btn text="Vissza" rounded="pill" @click="isModifyingExercise = false"></v-btn>
                <v-btn text="Módosítás" type="submit" variant="tonal" rounded="pill" :loading="isExerciseModificationLoading" @click="onExerciseModificationSubmission"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isStoppingGame" max-width="500">
        <v-card class="rounded-xl" title="Megerősítés">
            <v-card-text>
                <p>
                    Biztosan le akarod állítani a versenyt?
                </p>
            </v-card-text>
            <v-card-actions class="justify-space-between ml-5 mr-5 mb-2">
                <v-btn text="Vissza" rounded="pill" @click="isStoppingGame = false"></v-btn>
                <v-btn text="Leállítás" color="red" variant="tonal" rounded="pill" @click="stopGame"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
<script setup>
    import { ref, toRaw, computed, onMounted } from 'vue';
    import {
        difficultyDescriptions,
        difficultyNumLevels,
        getApiBasePath,
        nameRules,
        difficultyRules,
        difficultyItems,
        checkTeamNameAvailability
    } from "@/common/common";

    const apiBasePath = getApiBasePath();

    const teamHeaders = [
        {
            title: "Csapatnév",
            value: "name",
            key: "name"
        },
        {
            title: "Választott nehézség",
            value: item => difficultyDescriptions[item.difficulty],
            key: "difficulty"
        },
        {
            title: "Aktuális feladat",
            value: item => item.currentLevel <= difficultyNumLevels[item.difficulty] ? item.currentLevel : "Végzett",
            key: "currentLevel"
        },
        {
            title: "Kezelés",
            key: "actions",
            sortable: false,
            align: "end"
        }
    ]

    const exerciseHeaders = [
        {
            title: "Sorszám",
            value: "level",
            key: "level"
        },
        {
            title: "Cím",
            value: "title",
            key: "title"
        },
        {
            title: "Megoldás",
            value: "solution",
            key: "solution"
        },
        {
            title: "Kezelés",
            key: "actions",
            sortable: false,
            align: "end"
        }
    ]

    const GameStatus = {
        Stopped: 0,
        Started: 1
    };

    const statusNames = {
        [GameStatus.Stopped]: "Leállítva",
        [GameStatus.Started]: "Elindítva"
    }
    
    const statusColors = {
        [GameStatus.Stopped]: "gray",
        [GameStatus.Started]: "green"
    }

    const teamModificationForm = ref(null);
    const exerciseModificationForm = ref(null);
    const teams = ref([]);
    const exercises = ref([]);
    const didEncounterError = ref(false);
    const errorMessage = ref("");
    const teamBeingDeleted = ref(null);
    const modifiedTeam = ref(null);
    const originalTeam = ref(null);
    const exerciseBeingDeleted = ref(null);
    const modifiedExercise = ref(null);
    const originalExercise = ref(null);
    const isDeletingTeam = ref(false);
    const isModifyingTeam = ref(false);
    const isReloadingTeams = ref(true);
    const isStoppingGame = ref(false);
    const isTeamModificationLoading = ref(false);
    const isGameStateLoading = ref(false);
    const isGameStopLoading = ref(false);
    const isGameStartLoading = ref(false);
    const isDeletingExercise = ref(false);
    const isModifyingExercise = ref(false);
    const isReloadingExercises = ref(false);
    const isExerciseModificationLoading = ref(false);
    const teamNameAsyncError = ref("");
    const exerciseTitleAsyncError = ref("");
    const gameState = ref(null);

    const isFinished = computed({
        get() {
            return modifiedTeam.value.currentLevel > difficultyNumLevels[modifiedTeam.value.difficulty];
        },
        set(val) {
            const numLevels = difficultyNumLevels[modifiedTeam.value.difficulty]
            modifiedTeam.value.currentLevel = val ? numLevels + 1 : numLevels;
        }
    });

    const isStatusChangeLoading = computed({
        get() {
            return isGameStartLoading.value || isGameStopLoading.value;
        }
    })

    onMounted(async () => {
        reloadEverything();
    });

    function couldntGetTeams() {
        errorMessage.value = "Hiba történt a csapatok lekérdezése közben, próbáld meg újra";
        didEncounterError.value = true;
        isReloadingTeams.value = false;
    }

    function couldntGetExercises() {
        errorMessage.value = "Hiba történt a feladatok lekérdezése közben, próbáld meg újra";
        didEncounterError.value = true;
        isReloadingExercises.value = false;
    }

    function couldntRemoveTeam() {
        errorMessage.value = "Hiba történt a csapat törlése során";
        didEncounterError.value = true;
        isDeletingTeam.value = false;
    }

    function couldntModifyTeam() {
        errorMessage.value = "Hiba történt a csapat módosítása során";
        didEncounterError.value = true;
        isTeamModificationLoading.value = false;
    }

    function couldntDeleteExercise() {
        errorMessage.value = "Hiba történt a feladat törlése során";
        didEncounterError.value = true;
        isDeletingExercise.value = false;
    }

    function couldntModifyExercise() {
        errorMessage.value = "Hiba törént a feladat módosítása során";
        didEncounterError.value = true;
        isExerciseModificationLoading.value = false;
    }

    async function getTeams() {
        isReloadingTeams.value = true;
        await fetch(new URL("/teams", apiBasePath), {
            method: "GET",
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntGetTeams();
            }
            else {
                const result = await response.json();
                teams.value = result;
                isReloadingTeams.value = false;
            }
        },
        (error) => {
            couldntGetTeams();
        });
    }

    async function getExercises() {
        isReloadingExercises.value = true;
        await fetch(new URL("/exercises", apiBasePath), {
            method: "GET",
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntGetExercises();
            }
            else {
                const result = await response.json();
                exercises.value = result;
                isReloadingExercises.value = false;
            }
        },
        (error) => {
            couldntGetExercises();
        });
    }

    async function deleteTeam(team) {
        await fetch(new URL("/teams/delete", apiBasePath), {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                teamUuid: team.uuid
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntRemoveTeam();
            }
            else {
                isDeletingTeam.value = false;
                getTeams();
            }
        },
        (error) => {
            couldntRemoveTeam();
        });
    }

    async function sendTeamModification() {
        await fetch(new URL("/teams/modify", apiBasePath), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                teamUuid: modifiedTeam.value.uuid,
                newTeamName: modifiedTeam.value.name,
                newDifficulty: modifiedTeam.value.difficulty,
                newLevel: modifiedTeam.value.currentLevel
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntModifyTeam();
            }
            else {
                isModifyingTeam.value = false;
                getTeams();
            }
        },
        (error) => {
            couldntModifyTeam();
        });
    }

    async function deleteExercise(exercise) {
        await fetch(new URL("/exercises/delete", apiBasePath), {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                level: exercise.level
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntDeleteExercise();
            }
            else {
                isDeletingExercise.value = false;
                getExercises();
            }
        },
        (error) => {
            couldntDeleteExercise();
        });
    }

    async function sendExerciseModification() {
        await fetch(new URL("/exercises/modify", apiBasePath), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                level: originalExercise.value.level,
                newLevel: modifiedExercise.value.level,
                newTitle: modifiedExercise.value.title,
                newSolution: modifiedExercise.value.solution
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntModifyExercise();
            }
            else {
                isModifyingExercise.value = false;
                getExercises();
            }
        },
        (error) => {
            couldntModifyExercise();
        });
    }

    async function getGameState() {
        isGameStateLoading.value = true;
        await fetch(new URL("/state", apiBasePath), {
            method: "GET",
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntGetGameState();
            }
            else {
                gameState.value = await response.json();
                isGameStateLoading.value = false;
            }
        },
        (error) => {
            couldntGetGameState();
        });
    }

    async function startGame() {
        changeGameStatus(
            GameStatus.Started,
            isGameStartLoading,
            'Hiba történt a verseny indítása során'
        );
    }

    async function stopGame() {
        isStoppingGame.value = false;
        changeGameStatus(
            GameStatus.Stopped,
            isGameStopLoading,
            'Hiba történt a verseny leállítása során'
        );
    }

    async function changeGameStatus(newStatus, loadingIndicator, errorMessageText) {
        const couldntChangeGameStatus = () => {
            errorMessage.value = errorMessageText
            didEncounterError.value = true;
            loadingIndicator.value = false;
        }

        loadingIndicator.value = true;
        await fetch(new URL("/control", apiBasePath), {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                newStatus: newStatus
            }),
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntChangeGameStatus();
            }
            else {
                loadingIndicator.value = false;
                await getGameState();
            }
        },
        (error) => {
            couldntChangeGameStatus();
        });
    }

    async function handleTeamNameAvailability() {
        console.log(originalTeam.value.name, modifiedTeam.value.name)
        if (modifiedTeam.value.name == originalTeam.value.name) {
            return true;
        }

        let isTeamNameAvailable = false;
        await checkTeamNameAvailability(modifiedTeam.value.name).then(
            (available) => {
                if (available) {
                    teamNameAsyncError.value = "";
                    isTeamNameAvailable = true;
                }
                else {
                    teamNameAsyncError.value = "Ez a csapatnév már foglalt";
                    isTeamModificationLoading.value = false;
                    isTeamNameAvailable = false;
                }
            }
        ).catch(
            (reason) => {
                errorMessage.value = "Hiba történt a csapatnév ellenőrzése során, próbáld meg újra"
                didEncounterError.value = true;
                isTeamNameAvailable = false;
            }
        )

        return isTeamNameAvailable;
    };

    async function reloadEverything() {
        getTeams();
        getExercises();
        getGameState();
    }

    async function confirmTeamDeletion(teamRef) {
        const team = toRaw(teamRef);
        teamBeingDeleted.value = team;
        isDeletingTeam.value = true;
    }

    async function confirmExerciseDeletion(exerciseRef) {
        const exercise = toRaw(exerciseRef);
        exerciseBeingDeleted.value = exercise;
        isDeletingExercise.value = true;
    }

    async function openTeamModificationDialog(teamRef) {
        const team = structuredClone(toRaw(teamRef));
        modifiedTeam.value = team;
        originalTeam.value = structuredClone(team);
        isTeamModificationLoading.value = false;
        isModifyingTeam.value = true;
    }

    async function openExerciseModificationDialog(exerciseRef) {
        const exercise = structuredClone(toRaw(exerciseRef));
        modifiedExercise.value = exercise;
        originalExercise.value = structuredClone(exercise);
        isExerciseModificationLoading.value = false;
        isModifyingExercise.value = true;
    }

    async function onTeamModificationSubmission() {
        teamNameAsyncError.value = "";
        const { valid } = await teamModificationForm.value.validate();
        if (!valid) {
            return;
        }
        isTeamModificationLoading.value = true;

        const isTeamNameAvailable = await handleTeamNameAvailability();
        if (!isTeamNameAvailable) {
            isTeamModificationLoading.value = false;
            teamNameAsyncError.value = "Ez a csapatnév már foglalt";
            return;
        }

        await sendTeamModification();
    }

    async function onExerciseModificationSubmission() {
        exerciseTitleAsyncError.value = "";
        const { valid } = await exerciseModificationForm.value.validate();
        if (!valid) {
            return;
        }
        isTeamModificationLoading.value = true;

        await sendExerciseModification();
    }

</script>
<style>
    .table {
        max-width: 1000px;
    }
</style>
