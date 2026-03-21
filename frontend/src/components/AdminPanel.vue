<template>
    <div class="d-flex flex-column align-center justify-top mt-5 pa-5">
        <h1>Kezelőfelület</h1>
        <p class="ma-0">Csapatok száma: {{ teams.length }}</p>
        <v-data-table v-if="teams" class="mt-5 rounded-lg" :headers="teamHeaders" :items="teams"></v-data-table>
        <v-progress-circular v-else />
        <v-snackbar v-model="didEncounterError" color="red">
            {{ errorMessage }}
        </v-snackbar>
    </div>
</template>
<script setup>
    import { ref, onMounted } from 'vue';
    import { difficultyDescriptions, difficultyNumLevels, getApiBasePath } from "@/common/common";

    const apiBasePath = getApiBasePath();

    const teamHeaders = [
        {title: "Csapatnév", value: "name", key: "name"},
        {title: "Választott nehézség", value: item => difficultyDescriptions[item.difficulty], key: "difficulty"},
        {title: "Aktuális feladat", value: item => item.currentLevel <= difficultyNumLevels[item.difficulty] ? item.currentLevel : "Végzett", key: "currentLevel"}
    ]

    const teams = ref([
        {
            name: "Csapat1",
            difficulty: "Nehezebb",
            currentLevel: "5"
        }
    ])
    const didEncounterError = ref(false);
    const errorMessage = ref("");

    onMounted(async () => {
        await getTeams();
    });

    function couldntGetTeams() {
        errorMessage.value = "Hiba történt a csapatok lekérdezése közben, frissítsd újra az oldalt";
        didEncounterError.value = true;
    }

    async function getTeams() {
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
            }
        },
        (error) => {
            couldntGetTeams();
        });
    }
</script>