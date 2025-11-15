import React, { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { PasswordInput } from "@/components/ui/password-input";
import { useI18n } from "@/hooks/useI18n";

interface SettingsDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    currentApiUrl: string;
    currentAssistantId: string;
    currentApiKey: string;
    onSave: (apiUrl: string, assistantId: string, apiKey: string) => void;
}

export function SettingsDialog({
    open,
    onOpenChange,
    currentApiUrl,
    currentAssistantId,
    currentApiKey,
    onSave,
}: SettingsDialogProps) {
    const { t } = useI18n();
    const [apiUrl, setApiUrl] = useState(currentApiUrl);
    const [assistantId, setAssistantId] = useState(currentAssistantId);
    const [apiKey, setApiKey] = useState(currentApiKey);

    const handleSave = () => {
        onSave(apiUrl, assistantId, apiKey);
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>{t("settings.title")}</DialogTitle>
                </DialogHeader>
                <div className="flex flex-col gap-6 py-4">
                    <div className="flex flex-col gap-2">
                        <Label htmlFor="apiUrl">
                            {t("config.deploymentUrl")}
                            <span className="text-rose-500">{t("config.required")}</span>
                        </Label>
                        <p className="text-muted-foreground text-sm">
                            {t("config.deploymentUrlDesc")}
                        </p>
                        <Input
                            id="apiUrl"
                            value={apiUrl}
                            onChange={(e) => setApiUrl(e.target.value)}
                            placeholder="http://localhost:2024"
                        />
                    </div>

                    <div className="flex flex-col gap-2">
                        <Label htmlFor="assistantId">
                            {t("config.assistantId")}
                            <span className="text-rose-500">{t("config.required")}</span>
                        </Label>
                        <p className="text-muted-foreground text-sm">
                            {t("config.assistantIdDesc")}
                        </p>
                        <Input
                            id="assistantId"
                            value={assistantId}
                            onChange={(e) => setAssistantId(e.target.value)}
                            placeholder="agent"
                        />
                    </div>

                    <div className="flex flex-col gap-2">
                        <Label htmlFor="apiKey">{t("config.apiKey")}</Label>
                        <p className="text-muted-foreground text-sm">
                            {t("config.apiKeyDesc")}
                        </p>
                        <PasswordInput
                            id="apiKey"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder={t("config.apiKeyPlaceholder")}
                        />
                    </div>

                    <div className="flex justify-end gap-3">
                        <Button variant="outline" onClick={() => onOpenChange(false)}>
                            {t("common.cancel")}
                        </Button>
                        <Button onClick={handleSave}>{t("common.save")}</Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
