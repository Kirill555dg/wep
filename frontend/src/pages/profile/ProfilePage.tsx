import { useUserStore } from "@/entities/user/model/store";
import { useState } from "react";
import { profileApi } from "@/features/profile/api/profile-api";
import type { UserRole } from "@/entities/user/model/types";
import { useNavigate } from "react-router-dom";
import { MainLayout } from "@/widgets/layout/MainLayout";
import { Button } from "@/shared/ui/button";
import { Calendar, Mail, MapPin, Phone, User as UserIcon, Pencil } from "lucide-react";
import { ProfileAvatarBlock } from "./ui/ProfileAvatarBlock";
import { ProfileEditableField } from "./ui/ProfileEditableField";
import { getFullNameAdaptive } from "@/entities/user/lib/format";
import { SocialIcon } from "@/shared/ui/social-icon";
import { GenderEditableField } from "./ui/GenderEditableField";

export default function ProfilePage() {
  const user = useUserStore((s) => s.user);
  const setUser = useUserStore((s) => s.setUser);
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState(() => ({
    ...user!,
    phone: user?.phone || "",
    address: user?.address || "",
    about: user?.about || "",
    birthDate: user?.birthDate || "",
    gender: user?.gender,
    telegram: user?.contacts?.telegram || "",
    vk: user?.contacts?.vk || "",
  }));

  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const navigate = useNavigate();

  if (!user) return null;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const result = await profileApi.updateProfile({
        ...formData,
        contacts: {
          telegram: formData.telegram,
          vk: formData.vk,
        },
      });
      setUser(result);
      setIsEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      ...user,
      phone: user.phone || "",
      address: user.address || "",
      about: user.about || "",
      birthDate: user.birthDate || "",
      gender: user.gender,
      telegram: user.contacts?.telegram || "",
      vk: user.contacts?.vk || "",
    });
    setAvatarFile(null);
    setIsEditing(false);
  };

  const handleAvatarChange = (file: File | null) => {
    if (!file) return;
    setAvatarFile(file);
    const url = URL.createObjectURL(file);
    setFormData((prev) => ({ ...prev, avatar: url }));
  };

  const handleRoleSwitch = async (role: UserRole) => {
    const result = await profileApi.updateProfile({ ...user, role });
    setUser(result);
    navigate(`/${role}`);
  };

  return (
    <MainLayout title="Профиль" footer="full" back={{ label: "На главную", to: "/" }}>
      <div className="bg-white p-4 sm:p-6 sm:rounded-lg sm:shadow sm:border">
        <div className="flex flex-col md:flex-row gap-8">
          <ProfileAvatarBlock
            fullName={getFullNameAdaptive(user, true)}
            avatarUrl={formData.avatar || user.avatar}
            isEditing={isEditing}
            activeRole={formData.role}
            onSwitchRole={handleRoleSwitch}
            onAvatarChange={handleAvatarChange}
          />

          <div className="flex-1">
            <div className="flex justify-between items-center mb-6 flex-wrap gap-2">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <UserIcon className="h-5 w-5 text-muted-foreground" />
                Личная информация
              </h3>
              {isEditing ? (
                <div className="flex gap-2">
                  <Button variant="outline" onClick={handleCancel}>
                    Отмена
                  </Button>
                  <Button onClick={handleSave} disabled={saving}>
                    {saving ? "Сохранение..." : "Сохранить"}
                  </Button>
                </div>
              ) : (
                <Button size="sm" variant="ghost" onClick={() => setIsEditing(true)}>
                  <Pencil className="h-4 w-4 mr-1" />
                  Редактировать
                </Button>
              )}
            </div>

            <div className="space-y-6">
              <ProfileEditableField
                id="lastName"
                label="Фамилия"
                value={isEditing ? formData.lastName : user.lastName}
                onChange={handleChange}
                isEditing={isEditing}
              />
              <ProfileEditableField
                id="firstName"
                label="Имя"
                value={isEditing ? formData.firstName : user.firstName}
                onChange={handleChange}
                isEditing={isEditing}
              />
              <ProfileEditableField
                id="middleName"
                label="Отчество"
                value={isEditing ? formData.middleName || "" : user.middleName || ""}
                onChange={handleChange}
                isEditing={isEditing}
              />
              <ProfileEditableField
                id="birthDate"
                label="Дата рождения"
                type="date"
                icon={<Calendar className="h-4 w-4" />}
                value={isEditing ? formData.birthDate : user.birthDate || ""}
                onChange={handleChange}
                isEditing={isEditing}
              />
              <GenderEditableField
                value={isEditing ? formData.gender : user.gender || "male"}
                isEditing={isEditing}
                onChange={(val) => setFormData((prev) => ({ ...prev, gender: val }))}
              />
              <ProfileEditableField
                id="about"
                label="О себе"
                multiline
                value={isEditing ? formData.about : user.about || ""}
                onChange={handleChange}
                isEditing={isEditing}
              />
            </div>

            <div className="mt-10 mb-6 border-t pt-6">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Mail className="h-5 w-5 text-muted-foreground" />
                Контакты
              </h3>

              <div className="space-y-6 mt-4">
                <ProfileEditableField
                  id="email"
                  label="Email"
                  type="email"
                  icon={<Mail className="h-4 w-4" />}
                  value={user.email}
                  onChange={() => {}}
                  isEditing={false}
                />
                <ProfileEditableField
                  id="phone"
                  label="Телефон"
                  icon={<Phone className="h-4 w-4" />}
                  value={isEditing ? formData.phone : user.phone || ""}
                  onChange={handleChange}
                  isEditing={isEditing}
                />
                <ProfileEditableField
                  id="address"
                  label="Адрес"
                  icon={<MapPin className="h-4 w-4" />}
                  value={isEditing ? formData.address : user.address || ""}
                  onChange={handleChange}
                  isEditing={isEditing}
                />
                <ProfileEditableField
                  id="telegram"
                  label="Telegram"
                  icon={<SocialIcon type="telegram" className="h-4 w-4" />}
                  value={isEditing ? formData.telegram : user.contacts?.telegram || ""}
                  onChange={handleChange}
                  isEditing={isEditing}
                />
                <ProfileEditableField
                  id="vk"
                  label="VK"
                  icon={<SocialIcon type="vk" className="h-4 w-4" />}
                  value={isEditing ? formData.vk : user.contacts?.vk || ""}
                  onChange={handleChange}
                  isEditing={isEditing}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
