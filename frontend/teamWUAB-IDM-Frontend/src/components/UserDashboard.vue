<template>
    <v-container>
        <v-row>
            <v-col>
                <v-sheet rounded class="pa-6 rounded-lg d-flex flex-column text-center">
                    <div class="text-h1">{{ greetingMessage }}</div>
                    <div></div>
                </v-sheet>
            </v-col>
        </v-row>
        <user-granted-permissions v-if="activeUser" :active-user="activeUser"></user-granted-permissions>

    </v-container>
</template>

<script setup lang="ts">
    import { auth } from '@/store/auth';
    import {ref, Ref, computed, onMounted} from 'vue';
    import UserGrantedPermissions from './UserGrantedPermissions.vue';
import { Api } from '@/services/api';
import { User } from '@/assets/globalTypes';
    let periodOfDay: Ref<number> = ref(0)
    let activeUser: Ref<User | undefined> = ref()

    onMounted(() => {
        const date: Date = new Date()
        console.log(date.getHours())
        if (date.getHours() >= 19 || date.getHours() <= 2) {
            periodOfDay.value = 2
        } else if (date.getHours() >= 12 && date.getHours() < 19) {
            periodOfDay.value = 1
        } else {
            periodOfDay.value = 0
        }
        /*console.log(greetingMessages.value[periodOfDay.value])*/
    })

    const greetingMessage = computed(() => {
        switch (periodOfDay.value) {
            case 0:
                return 'Good morning!'
            case 1:
                return 'Good afternoon!'
            case 2:
                return 'Good evening!'
        }
    })
    Api.get('/show').then((res) => {
        activeUser.value = new User(
            res.user.uid,
            res.user.first_name,
            res.user.last_name,
            res.user.persistent_perms,
            res.user.requestable_resources,
            res.user.supervisors_uid,
        )
        for (let i: number = 0; i < res.user.active_perms.length; i++) {
            activeUser.value.active_perms.push(res.user.active_perms[i])
        }
        console.log(activeUser.value.active_perms)
        activeUser.value.active_perms.push({
            name: "Test",
            resource: "Test",
            expiry_time: Date.now() + 5000,
            is_inherent: false
        })
        console.log(activeUser.value)
    })

</script>
