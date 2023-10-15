<template>
<v-row>
    <v-col cols="12">
        <div class="text-h2 my-4">Current Status</div>
        <v-container style="overflow-x: auto;">
            <v-row>
                <v-col cols="12" md="4" v-for="(item, i) in permissionStatusList" v-if="typeof permissionStatusList !== 'string'" style="overflow-x: auto;">
                    <v-sheet class="pa-4 mr-4 rounded-lg bg-green" >
                <div class="text-h4">{{ item.name }}</div>
                <div class="text-subtitle-1 mb-4">{{ item.desc }}</div>

                <div class="text-body-1">Time Remaining: {{ Math.floor(item.timeRemainingInSeconds/60) }} minutes</div>
                <div class="text-body-1">Access Type: {{ item.accessType }}</div>
                </v-sheet>

                </v-col>
                <v-col v-else>
                    {{ permissionStatusList }}
                </v-col>
            </v-row>
        </v-container>
        <div class="flex-columns d-flex" style="overflow-x: auto;">

        </div>


    </v-col>
</v-row>
</template>

<script setup lang="ts">
import { User } from '@/assets/globalTypes';
import { UUID } from 'crypto';
import { computed } from 'vue';
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

let props = defineProps({
    activeUser: User
})

const userActivePerms = ref(props.activeUser?.active_perms)

let permissionStatusList: Ref<PermissionNode[]| string> = computed(() => {
    if (userActivePerms.value == undefined || userActivePerms.value[0] == undefined) {
        return "No Data"
    } else {
        let listOfPermissionNode: PermissionNode[] = []
        for (let i: number = 0; i < userActivePerms.value.length; i++) {
            listOfPermissionNode.push({
                desc: userActivePerms.value[i].name,
                name: userActivePerms.value[i].resource,
                timeRemainingInSeconds: userActivePerms.value[i].expiry_time - Date.now(),
                accessType: "inherent"
            })
            if (!userActivePerms.value[i].is_inherent) {
                listOfPermissionNode[i].accessType = 'onRequest'
            }
        }
        return listOfPermissionNode

    }
})

</script>
