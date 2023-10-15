<template>
<v-row>
    <v-col cols="12">
        <div class="text-h2 my-4">Current Status</div>
        <v-container style="overflow-x: auto;">
            <v-row>
                <v-col cols="12" md="4" v-for="(item, i) in permissionStatusList" style="overflow-x: auto;">
                    <v-sheet class="pa-4 mr-4 rounded-lg bg-green" >
                <div class="text-h4">{{ item.name }}</div>
                <div class="text-subtitle-1 mb-4">{{ item.desc }}</div>

                <div class="text-body-1">Time Remaining: {{ Math.floor(item.timeRemainingInSeconds/60) }} minutes</div>
                <div class="text-body-1">Access Type: {{ item.accessType }}</div>
            </v-sheet>
                
                </v-col>
            </v-row>
        </v-container>
        <div class="flex-columns d-flex" style="overflow-x: auto;">
            
        </div>

       
    </v-col>
</v-row>
</template>

<script setup lang="ts">
import { UUID } from 'crypto';
import { ref , Ref } from 'vue';
import { useDisplay, DisplayInstance } from 'vuetify/lib/framework.mjs';

const display: DisplayInstance = useDisplay()

const lgAndUp: Ref<boolean> = display.lgAndUp

type PermissionNode = {
    name: string,
    desc?: string,
    id?: UUID,
    timeRemainingInSeconds: number,
    accessType: "onRequest" | "inherent",
}

let permissionStatusList: Ref<PermissionNode[]> = ref([
    {
        name: "Access Protected B Data",
        id: '9551E631-ECF0-46B3-BCF0-625C73BE140F',
        timeRemainingInSeconds: 3000,
        desc: "Permission used to test the system",
        accessType: 'onRequest'
    },
    {
        name: "Access Protected A Data",
        id: '9551E631-ECF0-46B3-BCF0-625C73BE140F',
        timeRemainingInSeconds: 3000,
        desc: "Permission used to test the system",
        accessType: 'inherent'
    },
    {
        name: "Access Protected A Data",
        id: '9551E631-ECF0-46B3-BCF0-625C73BE140F',
        timeRemainingInSeconds: 3000,
        desc: "Permission used to test the system",
        accessType: 'onRequest'
    },
    {
        name: "Access Protected A Data",
        id: '9551E631-ECF0-46B3-BCF0-625C73BE140F',
        timeRemainingInSeconds: 3000,
        desc: "Permission used to test the system",
        accessType: 'onRequest'
    },
    {
        name: "Access Protected A Data",
        id: '9551E631-ECF0-46B3-BCF0-625C73BE140F',
        timeRemainingInSeconds: 3000,
        desc: "Permission used to test the system",
        accessType: 'onRequest'
    },
    {
        name: "Access Protected A Data",
        id: '9551E631-ECF0-46B3-BCF0-625C73BE140F',
        timeRemainingInSeconds: 3000,
        desc: "Permission used to test the system",
        accessType: 'onRequest'
    },
])

</script>