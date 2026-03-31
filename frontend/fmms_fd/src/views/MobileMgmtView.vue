<template>
  <div class="mobile-mgmt-page">
    <MobileTopbar title="家庭与物资管理" subtitle="统一管理家庭、成员和物资" :sticky="true">
      <template #leading>
        <button class="back-btn" type="button" aria-label="返回首页" @click="goHome">
          <img class="icon-img" src="https://api.iconify.design/solar/alt-arrow-left-linear.svg?color=%236b7280" alt="" aria-hidden="true">
        </button>
      </template>

      <template #actions>
        <button class="icon-btn" type="button" aria-label="设置" @click="goToSettings">
          <img class="icon-img" src="https://api.iconify.design/solar/settings-bold.svg?color=%236b7280" alt="" aria-hidden="true">
        </button>
        <button class="icon-btn" type="button" aria-label="退出登录" @click="handleLogout">
          <img class="icon-img" src="https://api.iconify.design/solar/logout-2-bold.svg?color=%236b7280" alt="" aria-hidden="true">
        </button>
      </template>
    </MobileTopbar>

    <main class="mobile-main">
      <section class="hero-card">
        <div>
          <span class="summary-chip">{{ families.length }} 个家庭</span>
          <h2>我的家庭</h2>
          <p>轻触卡片切换家庭，下面的物资列表会同步更新。</p>
        </div>
        <div class="hero-actions">
          <BaseButton variant="primary" :disabled="isCreatingFamily" @click="openFamilyModal">
            {{ isCreatingFamily ? '创建中...' : '创建家庭' }}
          </BaseButton>
          <BaseButton variant="ghost" :disabled="isLoadingFamilies || isLoadingItems" @click="refreshAll">
            刷新数据
          </BaseButton>
        </div>
      </section>

      <section class="content-section">
        <BaseEmptyState v-if="isLoadingFamilies" text="家庭列表加载中..." />
        <BaseEmptyState v-else-if="families.length === 0" :rich="true">
          <span>你还没有加入任何家庭，先创建一个新的家庭开始管理吧。</span>
          <BaseButton variant="primary" :disabled="isCreatingFamily" @click="openFamilyModal">
            立即创建家庭
          </BaseButton>
        </BaseEmptyState>

        <div v-else class="family-list">
          <article
            v-for="(family, index) in families"
            :key="family.id"
            class="family-card"
            :class="{ active: family.id === selectedFamilyId }"
            @click="selectFamily(family.id)"
          >
            <div class="family-cover" :style="getFamilyCoverStyle(index)">
              <span v-if="family.is_default" class="cover-badge">默认家庭</span>
            </div>

            <div class="family-body">
              <div class="family-main">
                <div class="family-title-row">
                  <h3>{{ family.name }}</h3>
                  <span v-if="family.role === 'owner'" class="badge badge-owner">Owner</span>
                </div>
                <p class="family-meta">
                  {{ family.role === 'owner' ? '你正在守护这个家园' : '你是这个家庭的协作成员' }}
                </p>
              </div>

              <div class="family-menu-wrap" @click.stop>
                <button
                  type="button"
                  class="menu-trigger"
                  aria-label="更多操作"
                  @click="toggleFamilyMenu(family.id)"
                >
                  <img
                    class="icon-img"
                    src="https://api.iconify.design/solar/menu-dots-bold.svg?color=%236b7280"
                    alt=""
                    aria-hidden="true"
                  >
                </button>

                <div v-if="activeFamilyMenuId === family.id" class="family-menu">
                  <button
                    type="button"
                    class="family-menu-item"
                    :disabled="family.is_default"
                    @click="setDefaultFamily(family)"
                  >
                    {{ family.is_default ? '当前已是默认家庭' : '设为默认家庭' }}
                  </button>
                  <button
                    v-if="family.role === 'owner'"
                    type="button"
                    class="family-menu-item"
                    :disabled="isManagingFamilyId === family.id"
                    @click="openMembersPanel(family)"
                  >
                    {{ isManagingFamilyId === family.id ? '成员加载中...' : '管理成员' }}
                  </button>
                  <button
                    type="button"
                    class="family-menu-item danger"
                    :disabled="isDeletingFamilyId === family.id"
                    @click="removeFamily(family)"
                  >
                    {{ isDeletingFamilyId === family.id ? '删除中...' : '删除家庭' }}
                  </button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="content-section inventory-section">
        <div class="section-head">
          <div>
            <h2>{{ selectedFamily ? selectedFamily.name : '当前家庭' }}</h2>
            <p>{{ selectedFamily ? '以下是当前家庭的全部物资。' : '请选择一个家庭查看物资。' }}</p>
          </div>
          <div class="section-actions">
            <BaseButton variant="ghost" :disabled="!selectedFamily || isLoadingItems" @click="loadItems">
              刷新物资
            </BaseButton>
            <BaseButton variant="primary" :disabled="!selectedFamily" @click="openItemModal()">
              新增物资
            </BaseButton>
          </div>
        </div>

        <BaseEmptyState v-if="!selectedFamily" text="先从上面的家庭卡片中选择一个家庭。" />
        <BaseEmptyState v-else-if="isLoadingItems" text="物资列表加载中..." />
        <BaseEmptyState v-else-if="filteredItems.length === 0" text="这个家庭还没有物资，点击上方按钮开始添加。" />

        <div v-else class="item-list">
          <article v-for="item in filteredItems" :key="item.id" class="item-card">
            <div class="item-head">
              <div>
                <h3>{{ item.name || '-' }}</h3>
                <p>{{ item.location || '-' }}</p>
              </div>
              <div class="item-actions">
                <BaseButton variant="text" @click="openItemModal(item)">编辑</BaseButton>
                <BaseButton variant="danger" @click="deleteItem(item)">删除</BaseButton>
              </div>
            </div>

            <dl class="item-meta-list">
              <div class="item-meta-row">
                <dt>描述</dt>
                <dd>{{ item.description || '-' }}</dd>
              </div>
              <div class="item-meta-row">
                <dt>到期时间</dt>
                <dd>{{ formatDate(item.expiration_date) }}</dd>
              </div>
              <div class="item-meta-row">
                <dt>创建时间</dt>
                <dd>{{ formatDate(item.created_at) }}</dd>
              </div>
            </dl>
          </article>
        </div>
      </section>
    </main>

    <BaseModal v-model="showMembersPanel" title="成员管理" :description="managingFamily?.name || ''" @close="closeMembersPanel">
      <BaseEmptyState v-if="isLoadingMembers" text="成员列表加载中..." />
      <BaseEmptyState v-else-if="members.length === 0" text="这个家庭暂时没有成员数据。" />
      <div v-else class="member-list">
        <article v-for="member in members" :key="member.id" class="member-card">
          <div class="member-main">
            <strong>{{ member.username }}</strong>
            <p>{{ member.email || member.phone || '未填写联系方式' }}</p>
          </div>
          <div class="member-actions">
            <select :value="member.role" @change="changeMemberRole(member, $event)">
              <option value="member">member</option>
              <option value="owner">owner</option>
            </select>
            <BaseButton variant="danger" :disabled="member.id === currentUserId" @click="removeMember(member)">
              移出家庭
            </BaseButton>
          </div>
        </article>
      </div>
    </BaseModal>

    <BaseModal
      v-model="showItemModal"
      :title="itemForm.id ? '编辑物资' : '新增物资'"
      :description="selectedFamily?.name || ''"
      @close="closeItemModal"
    >
      <form class="item-form" @submit.prevent="submitItem">
        <BaseFormField label="名称">
          <input v-model.trim="itemForm.name" type="text" maxlength="80" placeholder="例如：婴儿奶粉">
        </BaseFormField>
        <BaseFormField label="描述">
          <textarea v-model.trim="itemForm.description" rows="3" maxlength="240" placeholder="补充说明这件物品的规格、用途或注意事项"></textarea>
        </BaseFormField>
        <BaseFormField label="存放位置">
          <input v-model.trim="itemForm.location" type="text" maxlength="120" placeholder="例如：厨房右侧第二层">
        </BaseFormField>
        <BaseFormField label="到期时间">
          <input v-model="itemForm.expiration_date" type="datetime-local">
        </BaseFormField>

        <div class="form-actions">
          <BaseButton variant="ghost" @click="closeItemModal">取消</BaseButton>
          <BaseButton variant="primary" native-type="submit" :disabled="isSubmittingItem">
            {{ isSubmittingItem ? '提交中...' : '保存物资' }}
          </BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseModal v-model="showFamilyModal" title="创建家庭" description="创建后你会自动成为该家庭的 owner。" @close="closeFamilyModal">
      <form class="item-form" @submit.prevent="submitFamily">
        <BaseFormField label="家庭名称">
          <input v-model.trim="familyForm.name" type="text" maxlength="60" placeholder="例如：三口之家">
        </BaseFormField>

        <div class="form-actions">
          <BaseButton variant="ghost" @click="closeFamilyModal">取消</BaseButton>
          <BaseButton variant="primary" native-type="submit" :disabled="isCreatingFamily">
            {{ isCreatingFamily ? '创建中...' : '确认创建' }}
          </BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseConfirmDialog
      v-model="showDeleteItemConfirm"
      title="删除物资"
      description="这项操作不可撤销，请确认是否继续。"
      confirm-text="确认删除"
      loading-text="删除中..."
      :loading="isDeletingItem"
      :danger="true"
      @close="closeDeleteItemConfirm"
      @confirm="confirmDeleteItem"
    >
      <p>
        确认删除物资
        <strong>{{ deletingItem?.name || '' }}</strong>
        吗？
      </p>
    </BaseConfirmDialog>

    <BaseConfirmDialog
      v-model="showDeleteFamilyConfirm"
      title="删除家庭"
      description="删除后该家庭下的物资也会一并清空，请确认是否继续。"
      confirm-text="确认删除"
      loading-text="删除中..."
      :loading="Boolean(isDeletingFamilyId)"
      :danger="true"
      @close="closeDeleteFamilyConfirm"
      @confirm="confirmDeleteFamily"
    >
      <p>
        确认删除家庭
        <strong>{{ deletingFamily?.name || '' }}</strong>
        吗？
      </p>
    </BaseConfirmDialog>

    <BaseConfirmDialog
      v-model="showRemoveMemberConfirm"
      title="移出成员"
      description="移出后该成员将不再属于当前家庭。"
      confirm-text="确认移出"
      loading-text="移出中..."
      :loading="isRemovingMember"
      :danger="true"
      @close="closeRemoveMemberConfirm"
      @confirm="confirmRemoveMember"
    >
      <p>
        确认将
        <strong>{{ removingMember?.username || '' }}</strong>
        移出当前家庭吗？
      </p>
    </BaseConfirmDialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { message } from 'ant-design-vue'
import request from '@/utils/request'
import familyCover1 from '@/assets/family_1.png'
import familyCover2 from '@/assets/family_2.png'
import familyCover3 from '@/assets/family_3.png'
import BaseConfirmDialog from '@/components/BaseConfirmDialog.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseEmptyState from '@/components/BaseEmptyState.vue'
import BaseFormField from '@/components/BaseFormField.vue'
import BaseModal from '@/components/BaseModal.vue'
import MobileTopbar from '@/components/MobileTopbar.vue'

const router = useRouter()
const store = useStore()
const SHANGHAI_TIMEZONE = 'Asia/Shanghai'
const FAMILY_COVER_IMAGES = [familyCover1, familyCover2, familyCover3]

const families = ref([])
const items = ref([])
const members = ref([])
const selectedFamilyId = ref('')
const managingFamily = ref(null)
const showMembersPanel = ref(false)
const showItemModal = ref(false)
const showFamilyModal = ref(false)
const showDeleteItemConfirm = ref(false)
const showDeleteFamilyConfirm = ref(false)
const showRemoveMemberConfirm = ref(false)
const isLoadingFamilies = ref(false)
const isLoadingItems = ref(false)
const isLoadingMembers = ref(false)
const isSubmittingItem = ref(false)
const isCreatingFamily = ref(false)
const isDeletingItem = ref(false)
const isRemovingMember = ref(false)
const isDeletingFamilyId = ref('')
const isManagingFamilyId = ref('')
const activeFamilyMenuId = ref('')
const itemForm = ref(createEmptyItemForm())
const familyForm = ref(createEmptyFamilyForm())
const deletingItem = ref(null)
const deletingFamily = ref(null)
const removingMember = ref(null)

const currentUserId = computed(() => store.state.userInfo?.id || '')
const selectedFamily = computed(() => families.value.find((family) => family.id === selectedFamilyId.value) || null)
const filteredItems = computed(() => items.value.filter((item) => item.family_id === selectedFamilyId.value))

onMounted(async () => {
  document.addEventListener('click', handleDocumentClick)
  await loadFamilies()
  if (selectedFamilyId.value) {
    await loadItems()
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})

function createEmptyItemForm() {
  return {
    id: '',
    name: '',
    description: '',
    location: '',
    expiration_date: ''
  }
}

function createEmptyFamilyForm() {
  return {
    name: ''
  }
}

async function refreshAll() {
  await loadFamilies()
  if (selectedFamilyId.value) {
    await loadItems()
  }
}

async function loadFamilies() {
  isLoadingFamilies.value = true
  try {
    const response = await request.get('/user/families')
    families.value = Array.isArray(response) ? response : []

    if (families.value.length === 0) {
      selectedFamilyId.value = ''
      return
    }

    const hasSelected = families.value.some((family) => family.id === selectedFamilyId.value)
    if (!hasSelected) {
      const defaultFamily = families.value.find((family) => family.is_default)
      selectedFamilyId.value = (defaultFamily || families.value[0]).id
    }
  } catch (error) {
    console.error('Failed to load families:', error)
    families.value = []
    selectedFamilyId.value = ''
  } finally {
    isLoadingFamilies.value = false
  }
}

function openFamilyModal() {
  familyForm.value = createEmptyFamilyForm()
  showFamilyModal.value = true
}

function closeFamilyModal() {
  showFamilyModal.value = false
  familyForm.value = createEmptyFamilyForm()
}

async function submitFamily() {
  const name = familyForm.value.name.trim()

  if (!name) {
    message.warning('请先填写家庭名称')
    return
  }

  isCreatingFamily.value = true
  try {
    const created = await request.post('/user/families', { name })
    message.success('家庭创建成功')
    closeFamilyModal()
    await loadFamilies()

    if (created?.id) {
      selectedFamilyId.value = created.id
      await loadItems()
    }
  } catch (error) {
    console.error('Failed to create family:', error)
  } finally {
    isCreatingFamily.value = false
  }
}

async function loadItems() {
  if (!selectedFamilyId.value) {
    items.value = []
    return
  }

  isLoadingItems.value = true
  try {
    const response = await request.get('/item/items')
    items.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('Failed to load items:', error)
    items.value = []
  } finally {
    isLoadingItems.value = false
  }
}

async function selectFamily(familyId) {
  activeFamilyMenuId.value = ''
  if (familyId === selectedFamilyId.value) {
    return
  }

  selectedFamilyId.value = familyId
  await loadItems()
}

function toggleFamilyMenu(familyId) {
  activeFamilyMenuId.value = activeFamilyMenuId.value === familyId ? '' : familyId
}

function handleDocumentClick() {
  activeFamilyMenuId.value = ''
}

async function setDefaultFamily(family) {
  if (family.is_default) {
    activeFamilyMenuId.value = ''
    return
  }

  try {
    await request.put(`/user/families/default/${family.id}`)
    message.success('默认家庭已更新')
    selectedFamilyId.value = family.id
    activeFamilyMenuId.value = ''
    await loadFamilies()
    await loadItems()
  } catch (error) {
    console.error('Failed to set default family:', error)
  }
}

function removeFamily(family) {
  activeFamilyMenuId.value = ''
  deletingFamily.value = family
  showDeleteFamilyConfirm.value = true
}

function closeDeleteFamilyConfirm(force = false) {
  if (!force && isDeletingFamilyId.value) {
    return
  }

  showDeleteFamilyConfirm.value = false
  deletingFamily.value = null
}

async function confirmDeleteFamily() {
  if (!deletingFamily.value) {
    return
  }

  isDeletingFamilyId.value = deletingFamily.value.id
  try {
    await request.delete(`/user/families/${deletingFamily.value.id}`)
    message.success('家庭删除成功')
    if (managingFamily.value?.id === deletingFamily.value.id) {
      closeMembersPanel()
    }
    closeDeleteFamilyConfirm(true)
    await loadFamilies()
    await loadItems()
  } catch (error) {
    console.error('Failed to delete family:', error)
  } finally {
    isDeletingFamilyId.value = ''
  }
}

async function openMembersPanel(family) {
  activeFamilyMenuId.value = ''
  managingFamily.value = family
  showMembersPanel.value = true
  isManagingFamilyId.value = family.id
  await loadMembers(family.id)
  isManagingFamilyId.value = ''
}

function closeMembersPanel() {
  showMembersPanel.value = false
  managingFamily.value = null
  members.value = []
}

async function loadMembers(familyId) {
  isLoadingMembers.value = true
  try {
    const response = await request.get('/user/families/members', {
      params: { family_id: familyId }
    })
    members.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('Failed to load family members:', error)
    members.value = []
  } finally {
    isLoadingMembers.value = false
  }
}

async function changeMemberRole(member, event) {
  const nextRole = event.target.value
  if (!managingFamily.value || nextRole === member.role) {
    return
  }

  try {
    await request.put('/user/families/members/role', {
      family_id: managingFamily.value.id,
      member_id: member.id,
      role: nextRole
    })
    message.success('成员角色已更新')
    await Promise.all([loadMembers(managingFamily.value.id), loadFamilies()])
  } catch (error) {
    console.error('Failed to update member role:', error)
    event.target.value = member.role
  }
}

function removeMember(member) {
  if (!managingFamily.value) {
    return
  }

  removingMember.value = member
  showRemoveMemberConfirm.value = true
}

function closeRemoveMemberConfirm(force = false) {
  if (!force && isRemovingMember.value) {
    return
  }

  showRemoveMemberConfirm.value = false
  removingMember.value = null
}

async function confirmRemoveMember() {
  if (!managingFamily.value || !removingMember.value) {
    return
  }

  isRemovingMember.value = true
  try {
    await request.delete('/user/families/members', {
      data: {
        family_id: managingFamily.value.id,
        member_id: removingMember.value.id
      }
    })
    message.success('成员已移出家庭')
    closeRemoveMemberConfirm(true)
    await loadMembers(managingFamily.value.id)
  } catch (error) {
    console.error('Failed to remove member:', error)
  } finally {
    isRemovingMember.value = false
  }
}

function openItemModal(item) {
  itemForm.value = item
    ? {
        id: item.id || '',
        name: item.name || '',
        description: item.description || '',
        location: item.location || '',
        expiration_date: toDatetimeLocal(item.expiration_date)
      }
    : createEmptyItemForm()
  showItemModal.value = true
}

function closeItemModal() {
  showItemModal.value = false
  itemForm.value = createEmptyItemForm()
}

async function submitItem() {
  if (!selectedFamily.value) {
    return
  }

  if (!itemForm.value.name || !itemForm.value.location) {
    message.warning('请至少填写物资名称和存放位置')
    return
  }

  const payload = {
    name: itemForm.value.name,
    description: itemForm.value.description || null,
    location: itemForm.value.location,
    family_id: selectedFamily.value.id,
    expiration_date: normalizeDatetime(itemForm.value.expiration_date)
  }

  isSubmittingItem.value = true
  try {
    if (itemForm.value.id) {
      await request.put(`/item/items/${itemForm.value.id}`, {
        name: payload.name,
        description: payload.description,
        location: payload.location,
        expiration_date: payload.expiration_date
      })
      message.success('物资更新成功')
    } else {
      await request.post('/item/items', payload)
      message.success('物资添加成功')
    }
    closeItemModal()
    await loadItems()
  } catch (error) {
    console.error('Failed to submit item:', error)
  } finally {
    isSubmittingItem.value = false
  }
}

function deleteItem(item) {
  deletingItem.value = item
  showDeleteItemConfirm.value = true
}

function closeDeleteItemConfirm(force = false) {
  if (!force && isDeletingItem.value) {
    return
  }

  showDeleteItemConfirm.value = false
  deletingItem.value = null
}

async function confirmDeleteItem() {
  if (!deletingItem.value) {
    return
  }

  isDeletingItem.value = true
  try {
    await request.delete(`/item/items/${deletingItem.value.id}`)
    message.success('物资删除成功')
    closeDeleteItemConfirm(true)
    await loadItems()
  } catch (error) {
    console.error('Failed to delete item:', error)
  } finally {
    isDeletingItem.value = false
  }
}

function normalizeDatetime(value) {
  if (!value) {
    return null
  }

  const match = String(value).match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})(?::\d{2})?$/)
  if (!match) {
    return null
  }

  return `${match[1]} ${match[2]}:00`
}

function toDatetimeLocal(value) {
  const parts = getShanghaiDateParts(value)
  if (!parts) {
    return ''
  }

  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`
}

function formatDate(value) {
  const parts = getShanghaiDateParts(value)
  if (!parts) {
    return '-'
  }

  return `${parts.year}/${parts.month}/${parts.day} ${parts.hour}:${parts.minute}`
}

function getShanghaiDateParts(value) {
  if (!value) {
    return null
  }

  const text = String(value).trim()
  const plainMatch = text.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?$/)
  if (plainMatch) {
    return {
      year: plainMatch[1],
      month: plainMatch[2],
      day: plainMatch[3],
      hour: plainMatch[4],
      minute: plainMatch[5]
    }
  }

  const date = new Date(text)
  if (Number.isNaN(date.getTime())) {
    return null
  }

  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: SHANGHAI_TIMEZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
  const parts = formatter.formatToParts(date)
  const lookup = Object.fromEntries(parts.filter((part) => part.type !== 'literal').map((part) => [part.type, part.value]))

  return {
    year: lookup.year,
    month: lookup.month,
    day: lookup.day,
    hour: lookup.hour,
    minute: lookup.minute
  }
}

function handleLogout() {
  store.commit('CLEAR_TOKEN')
  router.push('/')
  message.success('已退出登录')
}

function goHome() {
  router.push('/m/home')
}

function goToSettings() {
  router.push('/settings')
}

function getFamilyCoverStyle(index) {
  const coverImage = FAMILY_COVER_IMAGES[index % FAMILY_COVER_IMAGES.length]

  return {
    backgroundImage: `linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.18)), url("${coverImage}")`,
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  }
}
</script>

<style scoped>
.mobile-mgmt-page {
  min-height: 100vh;
  min-height: 100dvh;
  background: radial-gradient(circle at 12% 0%, #f8f2eb 0%, #f7f5f2 36%, #f4f4f5 100%);
  color: #374151;
  font-family: 'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.back-btn,
.icon-btn {
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mobile-main {
  padding: 14px;
  padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 20px);
  display: grid;
  gap: 14px;
}

.hero-card,
.content-section {
  border: 1px solid #ebe5de;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.hero-card {
  padding: 18px;
  display: grid;
  gap: 14px;
}

.summary-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 7px 11px;
  background: #fcf8f3;
  color: #b1865b;
  font-size: 12px;
  border: 1px solid rgba(212, 176, 140, 0.35);
}

.hero-card h2,
.section-head h2 {
  margin: 12px 0 0;
  font-size: 20px;
  color: #1f2937;
}

.hero-card p,
.section-head p {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: #6b7280;
}

.hero-actions,
.section-actions,
.form-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.item-form .form-actions {
  justify-content: center;
  align-items: center;
}

.content-section {
  padding: 16px;
}

.family-list,
.item-list,
.member-list {
  display: grid;
  gap: 12px;
}

.family-card {
  border: 1px solid #f3ece4;
  background: linear-gradient(180deg, #ffffff 0%, #fcfaf7 100%);
  border-radius: 18px;
  overflow: visible;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.family-card.active {
  border-color: rgba(212, 176, 140, 0.5);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
}

.family-cover {
  height: 132px;
  border-bottom: 1px solid #f3ece4;
  position: relative;
  overflow: hidden;
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
}

.family-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.12) 45%, rgba(255,255,255,0.78) 100%);
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
}

.cover-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.92);
  color: #8f6746;
}

.family-body {
  padding: 14px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.family-main {
  min-width: 0;
}

.family-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.family-title-row h3,
.item-head h3 {
  margin: 0;
  font-size: 17px;
  color: #1f2937;
}

.family-meta,
.item-head p,
.member-main p {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: #6b7280;
}

.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
}

.badge-owner {
  background: #eff6ff;
  color: #1d4ed8;
}

.family-menu-wrap {
  position: relative;
  flex-shrink: 0;
}

.menu-trigger {
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.family-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 170px;
  max-width: min(220px, calc(100vw - 52px));
  border: 1px solid #f3f4f6;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.12);
  padding: 8px;
  display: grid;
  gap: 4px;
  z-index: 40;
}

.family-menu-item {
  width: 100%;
  border: 0;
  background: transparent;
  text-align: left;
  border-radius: 10px;
  padding: 10px 12px;
  color: #4b5563;
  font-size: 13px;
}

.family-menu-item.danger {
  color: #dc2626;
}

.inventory-section {
  display: grid;
  gap: 14px;
}

.section-head {
  display: grid;
  gap: 12px;
}

.item-card,
.member-card {
  border: 1px solid #f3f4f6;
  border-radius: 16px;
  background: #ffffff;
  padding: 14px;
}

.item-head {
  display: grid;
  gap: 10px;
}

.item-actions,
.member-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.item-meta-list {
  margin: 14px 0 0;
  display: grid;
  gap: 10px;
}

.item-meta-row {
  display: grid;
  gap: 4px;
}

.item-meta-row dt {
  font-size: 11px;
  font-weight: 700;
  color: #9ca3af;
}

.item-meta-row dd {
  margin: 0;
  font-size: 13px;
  color: #374151;
  line-height: 1.5;
}

.member-card {
  display: grid;
  gap: 12px;
}

.member-main strong {
  display: block;
  font-size: 15px;
  color: #1f2937;
}

.member-actions select,
.item-form :deep(input),
.item-form :deep(textarea) {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 11px 12px;
  font-size: 14px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
}

.member-actions select:focus,
.item-form :deep(input:focus),
.item-form :deep(textarea:focus) {
  border-color: #d4b08c;
  box-shadow: 0 0 0 3px rgba(212, 176, 140, 0.14);
}

.item-form {
  display: grid;
  gap: 14px;
}

.icon-img {
  width: 20px;
  height: 20px;
  display: block;
}

@media (max-width: 380px) {
  .mobile-main,
  .content-section,
  .hero-card {
    padding-left: 12px;
    padding-right: 12px;
  }

  .topbar-actions {
    gap: 8px;
  }

  .back-btn,
  .icon-btn {
    width: 34px;
    height: 34px;
  }
}
</style>
