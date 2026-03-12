<template>
    <div v-if="!isLoadingTeamInfo && teamResults"  class="d-flex flex-column align-center justify-top pa-5">
        <h1 class="text-center">Gratulálunk! {{ getLevelMessage() }}</h1>
        <p class="ma-1">Csapatnév: {{ teamInfo.teamName }}</p>
        <p class="ma-1">Nehézség: {{ difficultyDescriptions[teamInfo.difficulty] }}</p>
        <p class="ma-1">Összes csapatok száma: {{ teamResults.numTeams }}</p>
        <p class="ma-1">Csapatok száma akik végeztek: {{ teamResults.numFinishedTeams }}</p>
        <Teleport to="body">
            <div class="position-absolute confetti-wrapper">
                <ConfettiExplosion
                    v-if="doShowConfetti1"
                    :force="confettiForce1"
                    :stageWidth="confettiStageWidth1"
                    :stageHeight="confettiStageHeight1"
                    :duration="5000"
                />
                <ConfettiExplosion
                    v-if="doShowConfetti2"
                    :force="confettiForce2"
                    :stageWidth="confettiStageWidth2"
                    :stageHeight="confettiStageHeight2"
                    :colors="[
                        '#0038ff',
                        '#ffd050',
                        '#d14eae',
                        '#f03cf0'
                    ]"
                    :duration="5000"
                />
            </div>
        </Teleport>
    </div>
    <div v-else class="d-flex align-center justify-center h-100">
        <v-progress-circular class="align-center" indeterminate />
    </div>
    <v-snackbar v-model="didEncounterError" color="red">
        {{ errorMessage }}
    </v-snackbar>
</template>
<script setup>
    import { ref, onMounted, nextTick } from 'vue';
    import { Difficulty, difficultyDescriptions, difficultyNumLevels } from "@/constants/common";
    import ConfettiExplosion from "vue-confetti-explosion";

    const apiBasePath = `${window.location.protocol}//${window.location.hostname}:8000/`;
    const teamToken = localStorage.getItem("teamToken");

    if (teamToken === null) {
        window.location.href = "/regisztracio/";
    }

    const isLoadingTeamInfo = ref(true);
    const teamInfo = ref(null);
    const teamResults = ref(null);
    const didEncounterError = ref(false);
    const errorMessage = ref("");
    const doShowConfetti1 = ref(false);
    const doShowConfetti2 = ref(false);
    const confettiStageWidth1 = ref(0);
    const confettiStageWidth2 = ref(0);
    const confettiStageHeight1 = ref(0);
    const confettiStageHeight2 = ref(0);
    const confettiForce1 = ref(0);
    const confettiForce2 = ref(0);

    onMounted(async () => {
        await getTeamInfo();
        await getTeamResults();
        document.documentElement.classList.add('no-scroll');
        document.body.classList.add('no-scroll');
    });

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    function getLevelMessage() {
        if (teamInfo.value.difficulty === Difficulty.Hard && teamInfo.value.currentLevel - 1 === difficultyNumLevels[Difficulty.Hard]) {
            return "Megoldottátok az összes feladatot!";
        }
        else if (teamInfo.value.difficulty === Difficulty.Easy && teamInfo.value.currentLevel - 1 === difficultyNumLevels[Difficulty.Easy]) {
            return `Megoldottátok mind a ${difficultyNumLevels[Difficulty.Easy]} feladatot`;
        }
        else {
            return `Megoldottatok ${teamInfo.value.currentLevel - 1} feladatot a ${difficultyNumLevels[teamInfo.value.difficulty]} feladatból`;
        }
    }

    function getConfettiStageWidth() {
        const aspectRatio = window.innerWidth / window.innerHeight;
        const scale = 1 / Math.pow(aspectRatio, 0.4) + 0.2;
        return window.innerWidth * scale;
    }

    function getConfettiStageHeight() {
        return window.innerHeight * 2;
    }

    function getConfettiDelay() {
        return randomInRange(1000, 2000);
    }

    function getConfettiForce() {
        return randomInRange(0.5, 0.8);
    }

    async function startConfetti1() {
        confettiStageWidth1.value = getConfettiStageWidth();
        confettiStageHeight1.value = getConfettiStageHeight();
        confettiForce1.value = getConfettiForce();
        doShowConfetti1.value = false;
        await nextTick();
        doShowConfetti1.value = true;
        setTimeout(startConfetti2, getConfettiDelay());
    }

    async function startConfetti2() {
        confettiStageWidth2.value = getConfettiStageWidth();
        confettiStageHeight2.value = getConfettiStageHeight();
        confettiForce2.value = getConfettiForce();
        doShowConfetti2.value = false;
        await nextTick();
        doShowConfetti2.value = true;
        setTimeout(startConfetti1, getConfettiDelay());
    }

    function couldntGetTeamInfo() {
        errorMessage.value = "Hiba történt a csapat eredményeinek lekérdezése közben, frissítsd újra az oldalt";
        isLoadingTeamInfo.value = false;
        didEncounterError.value = true;
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

                if (result.currentLevel < 5) {
                    window.location.href = `/feladat/${result.currentLevel}`;
                }
                else {
                    teamInfo.value = result;
                    isLoadingTeamInfo.value = false;
                    startConfetti1();
                }
            }
        },
        (error) => {
            couldntGetTeamInfo();
        });
    }

    async function getTeamResults() {
        await fetch(new URL("/results", apiBasePath), {
            method: "GET",
            signal: AbortSignal.timeout(5000)
        }).then(async (response) => {
            if (!response.ok) {
                couldntGetTeamInfo();
            }
            else {
                const result = await response.json();

                teamResults.value = result;
                isLoadingTeamResults.value = false;
            }
        },
        (error) => {
            couldntGetTeamInfo();
        });
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