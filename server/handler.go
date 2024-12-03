package main

import (
	"encoding/json"
	"github.com/gorilla/mux"
	"net/http"
)

type Handler struct {
	conversionService *ConversionService
}

func NewHandler(cs *ConversionService) *Handler {
	return &Handler{
		conversionService: cs,
	}
}

func (h *Handler) HandleConversion(w http.ResponseWriter, r *http.Request) {
	var req ConversionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	job, err := h.conversionService.StartConversion(req.URL)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	response := ConversionResponse{
		JobID:         job.ID,
		Status:        job.Status,
		EstimatedTime: 30, // Estimate based on article length
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

	json.NewEncoder(w).Encode(ConversionResponse{
		JobID:  job.ID,
		Status: job.Status,
		Error:  job.Error,
	})
}

func (h *Handler) ListAudioFiles(w http.ResponseWriter, r *http.Request) {
	files, err := h.conversionService.ListAudioFiles()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"files": files,
	})
}
