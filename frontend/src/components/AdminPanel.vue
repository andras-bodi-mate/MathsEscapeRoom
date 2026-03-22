<template>
    <div class="d-flex flex-column align-center justify-top mt-5 pa-5">
        <h1>Kezelőfelület</h1>
        <div class="d-flex ga-2">
            <p class="ma-0">Csapatok száma: {{ isReloadingTeams ? "" : teams.length }}</p>
            <v-progress-circular v-if="isReloadingTeams" size="small" indeterminate></v-progress-circular>
        </div>
        <v-data-table class="table mt-5 rounded-xl overflow-hidden pa-5 ma-5" :headers="teamHeaders" :items="teams" :loading="isReloadingTeams">
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
        <v-btn prepend-icon="mdi-reload" :loading="isReloadingTeams" @click="reloadTeams">Frissítés</v-btn>
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
        <v-card class="rounded-xl" title="Módosítás" :loading="isModificationLoading">
            <v-card-text>
                <v-form ref="modificationForm" >
                    <v-text-field
                        v-model="modifiedTeam.name"
                        label="Új csapatnév"
                        :rules="nameRules"
                        :error-messages="teamNameAsyncError"
                        :disabled="isModificationLoading"
                        required
                    />
                    <v-select
                        v-model="modifiedTeam.difficulty"
                        label="Új nehézség"
                        item-title="label"
                        item-value="value"
                        :items="difficultyItems"
                        :rules="difficultyRules"
                        :disabled="isModificationLoading"
                        @update:modelValue="modifiedTeam.currentLevel = Math.min(
                            difficultyNumLevels[modifiedTeam.difficulty], modifiedTeam.currentLevel
                        )"
                    />
                    <div class="d-flex ga-5">
                        <v-number-input
                            v-model="modifiedTeam.currentLevel"
                            label="Aktuális feladat"
                            :min="1"
                            :max="difficultyNumLevels[modifiedTeam.difficulty]"
                            :disabled="isFinished"
                        >
                        </v-number-input>
                        <v-checkbox
                            v-model="isFinished"
                            label="Végzett"
                        >
                        </v-checkbox>
                    </div>
                </v-form>
            </v-card-text>
            <v-card-actions class="justify-space-between ml-5 mr-5 mb-2">
                <v-btn text="Vissza" rounded="pill" @click="isModifyingTeam = false"></v-btn>
                <v-btn text="Módosítás" type="submit" variant="tonal" rounded="pill" :loading="isModificationLoading" @click="onModificationSubmission"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
<script setup>
    import { ref, toRaw, reactive, computed, onMounted } from 'vue';
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
        {title: "Csapatnév", value: "name", key: "name"},
        {title: "Választott nehézség", value: item => difficultyDescriptions[item.difficulty], key: "difficulty"},
        {title: "Aktuális feladat", value: item => item.currentLevel <= difficultyNumLevels[item.difficulty] ? item.currentLevel : "Végzett", key: "currentLevel"},
        {title: "Kezelés", key: "actions", sortable: false, align: "end"}
    ]

    const modificationForm = ref(null);
    const teams = ref([])
    const didEncounterError = ref(false);
    const errorMessage = ref("");
    const teamBeingDeleted = ref(null);
    const modifiedTeam = ref(null);
    const originalTeam = ref(null);
    const isDeletingTeam = ref(false);
    const isModifyingTeam = ref(false);
    const isReloadingTeams = ref(true);
    const isModificationLoading = ref(false);
    const teamNameAsyncError = ref("");

    const isFinished = computed({
        get() {
            return modifiedTeam.value.currentLevel > difficultyNumLevels[modifiedTeam.value.difficulty];
        },
        set(val) {
            const numLevels = difficultyNumLevels[modifiedTeam.value.difficulty]
            modifiedTeam.value.currentLevel = val ? numLevels + 1 : numLevels;
        }
    });

    onMounted(async () => {
        await getTeams();
    });

    function couldntGetTeams() {
        errorMessage.value = "Hiba történt a csapatok lekérdezése közben, próbáld meg újra";
        didEncounterError.value = true;
        isReloadingTeams.value = false;
    }

    function couldntRemoveTeam() {
        errorMessage.value = "Hiba történt a csapat törlése során";
        didEncounterError.value = true;
    }

    function couldntModifyTeam() {
        errorMessage.value = "Hiba történt a csapat módosítása során";
        didEncounterError.value = true;
        isModificationLoading.value = false;
    }

    async function getTeams() {
        isReloadingTeams.value = true;
        teams.value = [];
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

    async function deleteTeam(team) {
        await fetch(new URL("/delete", apiBasePath), {
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

    async function sendModification() {
        await fetch(new URL("/modify", apiBasePath), {
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

    async function handleTeamNameAvailability() {
        await checkTeamNameAvailability(modifiedTeam.value.name).then(
            (available) => {
                if (available) {
                    teamNameAsyncError.value = "";
                    return true;
                }
                else {
                    teamNameAsyncError.value = "Ez a csapatnév már foglalt";
                    isModificationLoading.value = false;
                    return false;
                }
            }
        ).catch(
            (reason) => {
                errorMessage.value = "Hiba történt a csapatnév ellenőrzése során, próbáld meg újra"
                didEncounterError.value = true;
                return false;
            }
        )
    };

    async function reloadTeams() {
        await getTeams();
    }

    async function confirmTeamDeletion(teamRef) {
        const team = toRaw(teamRef);
        teamBeingDeleted.value = team;
        isDeletingTeam.value = true;
    }

    async function openTeamModificationDialog(teamRef) {
        const team = reactive(structuredClone(toRaw(teamRef)));
        console.log(team)
        modifiedTeam.value = team;
        originalTeam.value = team;
        isModificationLoading.value = false;
        isModifyingTeam.value = true;
    }

    async function onModificationSubmission() {
        teamNameAsyncError.value = "";
        const { valid } = await modificationForm.value.validate();
        if (!valid) {
            return;
        }
        isModificationLoading.value = true;

        const isTeamNameAvailable = modifiedTeam.value.name == originalTeam.value.name || await handleTeamNameAvailability();
        if (!isTeamNameAvailable) {
            isModificationLoading.value = false;
            return;
        }

        await sendModification();
    }

</script>
<style>
    .table {
        max-width: 1000px;
    }
</style>