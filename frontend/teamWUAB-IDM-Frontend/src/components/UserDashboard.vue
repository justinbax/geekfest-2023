<template>
    <v-container>
        <v-row>
            <v-col>
                <v-sheet rounded class="pa-6 rounded-lg d-flex flex-column text-center">
                    <div class="text-h1">{{ greetingMessage }}</div>
                    <v-btn @click="cheeseCount++" prepend-icon="mdi-cheese">Cheese Counter: {{ cheeseCount }}</v-btn>
                    <div></div>
                </v-sheet>
            </v-col>
        </v-row>
        <user-granted-permissions></user-granted-permissions>
        <v-row>
            <v-col>
                <v-card title="Request permission" class="pa-4" >
                    <v-card-text>
                        <v-select :items="['Test', 'Cheese']" v-model="selectedPermission"></v-select>
                        {{ selectedPermission }}
                    </v-card-text>
                </v-card>
            </v-col>
            <v-col>
                <v-card title="Settings" class="pa-4">
                    <v-slider step="5" max="120" v-model="durationInMinutes" :append="durationInMinutes">
                        <template v-slot:append>
                            {{ durationInMinutes }} minutes
                        </template>
                    </v-slider>
                    <v-textarea clearable label="Justification" v-model="justificationString"></v-textarea>
                    <v-btn @click="submit()">Submit!</v-btn>
                </v-card>
            </v-col>
        </v-row>
        <v-row>

        </v-row>
    </v-container>
</template>

<script setup lang="ts">
    import { auth } from '@/store/auth';
    import {ref, Ref, computed, onMounted} from 'vue';
    import UserGrantedPermissions from './UserGrantedPermissions.vue';
    let cheeseCount: Ref<number> = ref(0)
    let periodOfDay: Ref<number> = ref(0)
    let selectedPermission: Ref<string> = ref("Test")
    let durationInMinutes: Ref<number> = ref(5)
    let justificationString: Ref<string> = ref("")
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

    function submit(): void {
        console.log({
            permission: selectedPermission.value,
            duration: durationInMinutes.value,
            justification: justificationString.value,
            token: auth.account,
        })
    }

</script>