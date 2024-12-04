package api

import (
	"article2audio/internal/conversion"
	"encoding/json"
	"fmt"
	"github.com/gorilla/mux"
	"net/http"
)

type Handler struct {
	conversionService *conversion.AudioConverter // Changed from ConversionService
}

func NewHandler(cs *conversion.AudioConverter) *Handler { // Changed from ConversionService
	return &Handler{
		conversionService: cs,
	}
}

func (h *Handler) HandleConversion(w http.ResponseWriter, r *http.Request) {
	// Extract userID from context
	userID := r.Context().Value("userID").(string)

	var req conversion.ConversionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	job, err := h.conversionService.StartConversion(userID, req.URL)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	response := conversion.ConversionResponse{
		JobID:         job.ID,
		Status:        job.Status,
		EstimatedTime: 30,
	}

	json.NewEncoder(w).Encode(response)
}

func (h *Handler) GetConversionStatus(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := vars["jobId"]

	job, err := h.conversionService.GetStatus(jobID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	json.NewEncoder(w).Encode(conversion.ConversionResponse{ // Added conversion. prefix
		JobID:  job.ID,
		Status: job.Status,
		Error:  job.Error,
	})
}

func (h *Handler) ListAudioFiles(w http.ResponseWriter, r *http.Request) {
	userID := r.Context().Value("userID").(string)

	files, err := h.conversionService.ListAudioFiles(userID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	baseURL := "https://article2audio.s3.eu-west-1.amazonaws.com"

	response := struct {
		Files []struct {
			Key       string `json:"key"`
			URL       string `json:"url"`
			CreatedAt string `json:"createdAt"`
		} `json:"files"`
	}{
		Files: []struct {
			Key       string `json:"key"`
			URL       string `json:"url"`
			CreatedAt string `json:"createdAt"`
		}{},
	}

	for _, file := range files {
		response.Files = append(response.Files, struct {
			Key       string `json:"key"`
			URL       string `json:"url"`
			CreatedAt string `json:"createdAt"`
		}{
			Key:       file.Key,
			URL:       fmt.Sprintf("%s/%s", baseURL, file.Key),
			CreatedAt: file.CreatedAt,
		})
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
